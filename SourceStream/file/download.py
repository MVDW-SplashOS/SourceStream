from .. import SourceStream

from ..vendor.SplashPyUtils import logger

import requests
import os


def _drain(fh):
    """Read the whole stream so truncated transfers raise here."""
    while fh.read(1 << 20):
        pass


def _verify_archive(content, filename, package_name, package_version):
    """Fully decompress the archive in memory so a truncated or corrupt
    transfer is caught here instead of during a build much later."""
    import gzip, lzma, bz2, zipfile, tarfile, io

    try:
        if filename.endswith((".tar.gz", ".tgz")):
            _drain(gzip.GzipFile(fileobj=io.BytesIO(content)))
        elif filename.endswith(".tar.xz"):
            # lzma.LZMAFile has no fileobj parameter (unlike gzip/bz2), so
            # stream through LZMADecompressor: a corrupt stream raises
            # LZMAError, and a truncated transfer is caught by the eof check
            # (a valid xz stream must reach its end marker).
            d = lzma.LZMADecompressor()
            src = io.BytesIO(content)
            while True:
                chunk = src.read(1 << 20)
                if not chunk or d.eof:
                    break
                d.decompress(chunk)
            if not d.eof:
                raise RuntimeError("truncated xz stream")
        elif filename.endswith(".tar.bz2"):
            # bz2.BZ2File lost its fileobj parameter in Python 3.13; stream
            # through BZ2Decompressor (same reasoning as the xz branch).
            d = bz2.BZ2Decompressor()
            src = io.BytesIO(content)
            while True:
                chunk = src.read(1 << 20)
                if not chunk or d.eof:
                    break
                d.decompress(chunk)
            if not d.eof:
                raise RuntimeError("truncated bz2 stream")
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                bad = z.testzip()
                if bad is not None:
                    raise RuntimeError(f"corrupt zip member: {bad}")
        elif filename.endswith(".tar"):
            # plain tar has no integrity trailer; verify the member list
            with tarfile.open(fileobj=io.BytesIO(content)) as t:
                for _ in t:
                    pass
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"Archive for {package_name}({package_version}) failed the "
            f"integrity check: {type(e).__name__}: {e}"
        )


def expand_package_url(package_name, package_version):
    """Upstream URL of a package with every version placeholder expanded.

    Shared by download and repack: both must agree on the archive's file
    name in input/, otherwise a package whose file name uses a placeholder
    other than {VERSION} (icu4c-{VERSION_SEPARATE_UNDERSCORE}-src.tgz)
    downloads fine but cannot be found again when repacking.
    """
    package_version_split = package_version.split(".")

    url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version)
    url = url.replace("{VERSION_SEPARATE_UNDERSCORE}", package_version.replace(".", "_"))

    if(len(package_version_split) >= 1): url = url.replace("{VERSION_MAJOR}", package_version_split[0])
    if(len(package_version_split) >= 2): url = url.replace("{VERSION_MINOR}", package_version_split[1])
    if(len(package_version_split) >= 3): url = url.replace("{VERSION_REVISION}", package_version_split[2])
    if(len(package_version_split) >= 4): url = url.replace("{VERSION_BUILD}", package_version_split[3])
    return url


def download_tool(package):
    package_name = package["package"]
    package_version = package["version"]

    package_url = expand_package_url(package_name, package_version)

    package_filename = os.path.basename(package_url)
    package_path = os.path.join(SourceStream.DIR_INPUT, package_filename)

    if not os.path.exists(package_path):
        # Ask for the archive unencoded: some hosts (e.g. Netlify for
        # duktape.org) gzip-encode the transfer when the client advertises
        # gzip, which requests does by default. requests then returns the
        # decoded body, so its length never matches the (encoded)
        # Content-Length and the truncation check below fires falsely.
        r = requests.get(package_url, headers={"Accept-Encoding": "identity"})

        # Verify the download: some mirrors (e.g. SourceForge) truncate
        # transfers without an error, and a silently truncated archive gets
        # cached here and repacked into a corrupt package (tcl, 14 Nov 2026).
        expected = r.headers.get("Content-Length")
        if expected and len(r.content) != int(expected):
            raise RuntimeError(
                f"Download of {package_url} is truncated: got {len(r.content)} "
                f"of {expected} bytes."
            )
        _verify_archive(r.content, package_filename, package_name, package_version)

        open(package_path, 'wb').write(r.content)
        logger.log.ok(f"Downloaded package \x1b[1;37m{package_name}({package_version})\x1b[0m Successfully.")
