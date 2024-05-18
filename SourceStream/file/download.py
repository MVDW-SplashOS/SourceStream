from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import requests
import os

def download_tool(package):
    package_name = package["package"];
    package_version = package["version"];
    package_version_split = package["version"].split(".");

    package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version);
    package_url = package_url.replace("{VERSION_SEPARATE_UNDERSCORE}", package_version.replace(".", "_"));

    if(len(package_version_split) >= 1): package_url = package_url.replace("{VERSION_MAJOR}", package_version_split[0]);
    if(len(package_version_split) >= 2): package_url = package_url.replace("{VERSION_MINOR}", package_version_split[1]);
    if(len(package_version_split) >= 3): package_url = package_url.replace("{VERSION_REVISION}", package_version_split[2]);
    if(len(package_version_split) >= 4): package_url = package_url.replace("{VERSION_BUILD}", package_version_split[3]);

    package_filename = os.path.basename(package_url);
    package_path = os.path.join(SourceStream.DIR_INPUT, package_filename)

    if not os.path.exists(package_path):
        r = requests.get(package_url)
        open(package_path, 'wb').write(r.content)
        logger.log.ok("Downloaded package \x1b[1;37m" + package_name + "(" + package_version + ")\x1b[0m Successfully.")

