from .. import SourceStream

from ..vendor.SplashPyUtils import logger

import shutil
import subprocess
import tarfile
import os


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
    package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version)
    package_filename = os.path.basename(package_url)
    package_fullname = f"{package_name}-{package_version}"
    package_path_input = os.path.join(SourceStream.DIR_INPUT, package_filename)
    package_path_folder = os.path.join(SourceStream.DIR_INPUT, package_fullname)

    try:
        # Extract tar file in the input directory.
        with tarfile.open(package_path_input) as f:
            if not SourceStream.YAML_SOURCES[package_name]["subdir"]:
                os.makedirs(package_path_folder, exist_ok=True)
                f.extractall(package_path_folder)
            else:
                f.extractall(SourceStream.DIR_INPUT)

        # Check if the folder just extracted needs to be renamed.
        if isinstance(SourceStream.YAML_SOURCES[package_name]["subdir"], str):
            subdir = SourceStream.YAML_SOURCES[package_name]["subdir"].replace("{VERSION}", package_version).replace("{PACKAGE}", package_name)
            path_source = os.path.join(SourceStream.DIR_INPUT, subdir)
            os.rename(path_source, package_path_folder)

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