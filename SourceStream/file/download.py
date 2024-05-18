from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import requests
import os

def download_tool(package):
    package_name = package["package"];
    package_version = package["version"];
    package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version);
    package_url = package_url.replace("{VERSION_SEPARATE_UNDERSCORE}", package_version.replace(".", "_"));
    package_filename = os.path.basename(package_url);
    package_path = os.path.join(SourceStream.DIR_INPUT, package_filename)

    if not os.path.exists(package_path):
        r = requests.get(package_url)
        open(package_path, 'wb').write(r.content)
        logger.log.ok("Downloaded package \x1b[1;37m" + package_name + "(" + package_version + ")\x1b[0m Successfully.")

