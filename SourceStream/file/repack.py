from .. import SourceStream

from ..vendor.SplashPyUtils import logger

from . import download

import shutil
import subprocess
import tarfile
import os


def _clean(path):
    shutil.rmtree(path, ignore_errors=True)


def _verify_extracted(archive_path, folder):
    """Fail loudly when the extracted tree does not match the archive.

    A partial extraction (interrupted run, concurrent instance, stale
    leftovers) used to be repacked and pushed silently, producing corrupt
    packages that only fail later at build time (tcl/tcl_docs did exactly
    that on 14 Nov 2026). Paths are compared relative to the archive's
    top-level directory, since the tree may be renamed afterwards.
    """
    with tarfile.open(archive_path) as f:
        names = [m.name for m in f.getmembers() if not m.isdir()]
    names = [n[2:] if n.startswith("./") else n for n in names]
    tops = {n.split("/", 1)[0] for n in names if "/" in n}
    if len(tops) == 1:
        top = tops.pop()
        expected = {n[len(top) + 1:] for n in names if n.startswith(top + "/")}
    else:
        expected = set(names)

    got = set()
    for root, dirs, files in os.walk(folder):
        rel = os.path.relpath(root, folder)
        prefix = "" if rel == "." else rel.replace(os.sep, "/") + "/"
        for d in dirs:
            if os.path.islink(os.path.join(root, d)):
                got.add(prefix + d)
        got.update(prefix + name for name in files)

    missing = expected - got
    if missing:
        raise RuntimeError(
            f"extraction incomplete: {len(missing)} of {len(expected)} files "
            f"missing (e.g. {sorted(missing)[:3]}). The archive may be "
            f"truncated or another process touched the extraction directory."
        )


_CARGO_SOURCE_REPLACEMENT = """
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
"""


def _cargo_vendor(folder, package_name):
    """Vendor the Rust crates of a source tree for offline builds.

    Some upstream release tarballs (librsvg) need crates.io at build time,
    but packages are built in a chroot without network access. With
    `cargo_vendor: true` in upstream-sources.yml the crates are fetched
    here, into <source>/vendor, and .cargo/config.toml redirects crates-io
    to them, so the build script can run cargo --offline. --locked keeps
    the exact versions from the tarball's Cargo.lock. cargo vendor only
    downloads and unpacks crates; it does not run build scripts.
    """
    cargo = shutil.which("cargo")
    if not cargo:
        raise RuntimeError(f"{package_name} needs cargo_vendor, but cargo is not installed")
    if not os.path.exists(os.path.join(folder, "Cargo.lock")):
        raise RuntimeError(f"{package_name}: cargo_vendor is set but the source has no Cargo.lock")

    result = subprocess.run([cargo, "vendor", "--locked", "vendor"], cwd=folder,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"cargo vendor failed for {package_name}:\n{result.stderr.strip()}")

    config_dir = os.path.join(folder, ".cargo")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.toml")
    existing = ""
    if os.path.exists(config_path):
        with open(config_path) as f:
            existing = f.read()
    if "[source.crates-io]" not in existing:
        with open(config_path, "a") as f:
            f.write(_CARGO_SOURCE_REPLACEMENT)
    logger.log.info(f"Vendored the Rust crates of \x1b[1;37m{package_name}\x1b[0m.")


def _write_repacked_tar(tar, package_name, package_version, package_fullname):
    """Add the package source (plus BuildScripts extras) to an open tarfile."""
    tar.add(os.path.join(SourceStream.DIR_INPUT, package_fullname), arcname=package_fullname)

    # Check if configuration files exist for these packages
    if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version)):
        tar.add(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "manifest.yml"), arcname="manifest.yml")

        # Check if there are some extra folders included
        if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "build")):
            tar.add(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "build"), arcname="build")
        if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "patch")):
            tar.add(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "patch"), arcname="patch")

    else:
        logger.log.warn(f"The package {package_name} does not have a manifest.")


def repack_tool(packages):
    package_name = packages["package"]
    package_version = packages["version"]
    # Same expansion as the download step, or archives whose file name uses
    # another placeholder (icu4c-{VERSION_SEPARATE_UNDERSCORE}-src.tgz) are
    # looked for under an unexpanded name and the repack fails.
    package_url = download.expand_package_url(package_name, package_version)
    package_filename = os.path.basename(package_url)
    package_fullname = f"{package_name}-{package_version}"
    package_path_input = os.path.join(SourceStream.DIR_INPUT, package_filename)
    package_path_folder = os.path.join(SourceStream.DIR_INPUT, package_fullname)

    # Each package extracts into its own isolated staging directory. Two
    # packages whose upstream archives use the same inner directory name
    # (tcl and tcl_docs both use tcl<VERSION>/) must never share an
    # extraction directory — one would rename it away while the other is
    # still reading it, and both tarballs end up corrupt.
    staging = os.path.join(SourceStream.DIR_INPUT, f".staging-{package_fullname}")
    _clean(staging)
    os.makedirs(staging)

    try:
        # Extract tar file into the isolated staging directory.
        with tarfile.open(package_path_input) as f:
            f.extractall(staging)

        # Check if the folder just extracted needs to be renamed.
        if isinstance(SourceStream.YAML_SOURCES[package_name]["subdir"], str):
            subdir = SourceStream.YAML_SOURCES[package_name]["subdir"].replace("{VERSION}", package_version).replace("{PACKAGE}", package_name)
            path_source = os.path.join(staging, subdir)
        elif SourceStream.YAML_SOURCES[package_name]["subdir"] is False:
            # Multiple top-level entries (e.g. tzdata): the whole staging
            # dir becomes the package dir.
            path_source = staging
        else:
            # subdir: true -> the archive's own top-level dir, whatever it is
            tops = [n for n in os.listdir(staging) if os.path.isdir(os.path.join(staging, n))]
            if len(tops) != 1:
                raise RuntimeError(f"expected exactly one top-level dir in the archive, got: {tops}")
            path_source = os.path.join(staging, tops[0])

        _clean(package_path_folder)
        os.rename(path_source, package_path_folder)

        # Never pack a partially extracted tree.
        _verify_extracted(package_path_input, package_path_folder)

        # Rust sources whose release tarball does not ship its crates.
        if SourceStream.YAML_SOURCES[package_name].get("cargo_vendor"):
            _cargo_vendor(package_path_folder, package_name)

        # Create package directory where repacked tar file will be saved in.
        os.makedirs(os.path.join(SourceStream.DIR_OUTPUT, package_name), exist_ok=True)

        # Create tar file
        tar_path = os.path.join(SourceStream.DIR_OUTPUT, package_name, f"{package_fullname}.tar.xz")
        xz_bin = shutil.which("xz")
        if xz_bin:
            # tarfile's "w:xz" compresses single-threaded (~1.5 MB/s), which
            # takes ~10 min for linux/gcc-sized sources. Write an uncompressed
            # tar and compress with the xz binary using every core instead.
            plain_path = tar_path[:-len(".xz")]
            try:
                with tarfile.open(plain_path, "w") as tar:
                    _write_repacked_tar(tar, package_name, package_version, package_fullname)
                with open(plain_path, "rb") as src, open(tar_path, "wb") as dst:
                    result = subprocess.run([xz_bin, "-T0", "-c"], stdin=src, stdout=dst)
                if result.returncode != 0:
                    raise RuntimeError(f"xz exited with status {result.returncode}")
            finally:
                if os.path.exists(plain_path):
                    os.remove(plain_path)
        else:
            with tarfile.open(tar_path, "w:xz") as tar:
                _write_repacked_tar(tar, package_name, package_version, package_fullname)

        # Cleanup the input folder
        shutil.rmtree(package_path_folder)

        logger.log.ok(f"Repacked package \x1b[1;37m{package_name}({package_version})\x1b[0m Successfully.")
    except Exception as e:
        logger.log.fail(f"Error trying to repack package \x1b[1;37m{package_name}({package_version})\x1b[0m, Configuration error?\n{e}")
    finally:
        _clean(staging)