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
            _drain(bz2.BZ2File(fileobj=io.BytesIO(content)))
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


def download_tool(package):
    package_name = package["package"]
    package_version = package["version"]
    package_version_split = package["version"].split(".")

    package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version)
    package_url = package_url.replace("{VERSION_SEPARATE_UNDERSCORE}", package_version.replace(".", "_"))

    if(len(package_version_split) >= 1): package_url = package_url.replace("{VERSION_MAJOR}", package_version_split[0])
    if(len(package_version_split) >= 2): package_url = package_url.replace("{VERSION_MINOR}", package_version_split[1])
    if(len(package_version_split) >= 3): package_url = package_url.replace("{VERSION_REVISION}", package_version_split[2])
    if(len(package_version_split) >= 4): package_url = package_url.replace("{VERSION_BUILD}", package_version_split[3])

    package_filename = os.path.basename(package_url)
    package_path = os.path.join(SourceStream.DIR_INPUT, package_filename)

    if not os.path.exists(package_path):
        r = requests.get(package_url)

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
