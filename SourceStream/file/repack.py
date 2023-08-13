from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import shutil
import tarfile
import os

def repack_tool(tool, yaml_sources):
    package = tool["package"];
    version = tool["version"];
    url = yaml_sources[package]["url"].replace("{VERSION}", version);
    filename = os.path.basename(url);
    

    with tarfile.open(SourceStream.DIR_INPUT + filename) as f:
        if not yaml_sources[package]["subdir"]:
            os.makedirs(SourceStream.DIR_INPUT + package + "-" + version, exist_ok=True)
            f.extractall(SourceStream.DIR_INPUT + package + "-" + version)
        else:
            f.extractall(SourceStream.DIR_INPUT)

    if isinstance(yaml_sources[package]["subdir"], str):
        subdir = yaml_sources[package]["subdir"].replace("{VERSION}", version).replace("{PACKAGE}", package);
        os.rename(SourceStream.DIR_INPUT + subdir, SourceStream.DIR_INPUT + package + "-" + version); 

    os.makedirs(SourceStream.DIR_OUTPUT + package, exist_ok=True)
    with tarfile.open(SourceStream.DIR_OUTPUT + package + "/" + package + "-" + version + ".tar.xz", "w:xz") as tar:
        tar.add(SourceStream.DIR_INPUT + package + "-" + version, arcname=package + "-" + version)

        # Check if buildscript exist for these packages
        
        if os.path.exists(SourceStream.DIR_BUILTSCRIPTS + package):
            tar.add(SourceStream.DIR_BUILTSCRIPTS + package + "/manifest.yml", arcname="manifest.yml")

            # Check if there are some extra folders included 
            if os.path.exists(SourceStream.DIR_BUILTSCRIPTS + package + "/build"):
                tar.add(SourceStream.DIR_BUILTSCRIPTS + package + "/build", arcname="build")
            if os.path.exists(SourceStream.DIR_BUILTSCRIPTS + package + "/patch"):
                tar.add(SourceStream.DIR_BUILTSCRIPTS + package + "/patch", arcname="patch")
        else:
            logger.log.warn("The package " + package + " does not have a manifest.")

    shutil.rmtree(SourceStream.DIR_INPUT + package + "-" + version)
    logger.log.ok("Repacked package \x1b[1;37m" + package + "\x1b[0m Successfully.")