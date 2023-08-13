from ... import SourceStream;

from ...vendor.SplashPyUtils import logger

def run():

    package_list = []
    for package in SourceStream.YAML_EDITION["packages"]:
        package_name = package["package"];
        package_ver = "Version: " + package["version"]
        package_source = "Source: " + SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package["version"])

        package_list.append(package_name)
        package_list.append([package_ver, package_source]);

    
    logger.log.tree(package_list)
    exit(0)

