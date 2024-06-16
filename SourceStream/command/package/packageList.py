from ... import SourceStream

from ...vendor.SplashPyUtils import logger

def show(args):

    package_tree = []
    for package in SourceStream.YAML_EDITION["packages"]:
        package_name = package["package"]
        package_ver = f"Version: {package["version"]}"
        package_source = f"Source: {SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package["version"])}" 

        package_tree.append(package_name)
        package_tree.append([package_ver, package_source])

    
    logger.log.tree(package_tree)
    exit(0)

