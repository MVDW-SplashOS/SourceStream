from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import shutil
import tarfile
import os

def repack_tool(packages):
    package_name = packages["package"];
    package_version = packages["version"];
    package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version);
    package_filename = os.path.basename(package_url);
    package_fullname = package_name + "-" + package_version
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
            subdir = SourceStream.YAML_SOURCES[package_name]["subdir"].replace("{VERSION}", package_version).replace("{PACKAGE}", package_name);
            path_source = os.path.join(SourceStream.DIR_INPUT, subdir)
            os.rename(path_source, package_path_folder); 

        # Create package directory where repacked tar file will be saved in.
        os.makedirs(os.path.join(SourceStream.DIR_OUTPUT, package_name), exist_ok=True)

        # Create tar file
        with tarfile.open(os.path.join(SourceStream.DIR_OUTPUT, package_name, package_fullname + ".tar.xz"), "w:xz") as tar:
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
                logger.log.warn("The package " + package_name + " does not have a manifest.")

        # Cleanup the input folder
        shutil.rmtree(package_path_folder)

        logger.log.ok("Repacked package \x1b[1;37m" + package_name + "(" + package_version + ")\x1b[0m Successfully.")
    except Exception as e:
        logger.log.fail("Error trying to repack package \x1b[1;37m" + package_name + "(" + package_version + ")\x1b[0m, Configuration error?\n" + f"{e}")