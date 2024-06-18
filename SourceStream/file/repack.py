from .. import SourceStream

from ..vendor.SplashPyUtils import logger

import shutil
# import tarfile
import os
import subprocess

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
        subprocess.run(["tar", "-xf", package_path_input, "-C", SourceStream.DIR_INPUT], check=True)

        # Check if the folder just extracted needs to be renamed.
        if isinstance(SourceStream.YAML_SOURCES[package_name]["subdir"], str):
            subdir = SourceStream.YAML_SOURCES[package_name]["subdir"].replace("{VERSION}", package_version).replace("{PACKAGE}", package_name)
            path_source = os.path.join(SourceStream.DIR_INPUT, subdir)
            os.rename(path_source, package_path_folder) 

        # Create package directory where repacked tar file will be saved in.
        os.makedirs(os.path.join(SourceStream.DIR_OUTPUT, package_name), exist_ok=True)

       # Create a list of files and directories to be included in the tar file
        tar_items = [package_fullname]

        # Check if configuration files exist for these packages
        if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version)):
            tar_items.append(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "manifest.yml"))

            # Check if there are some extra folders included 
            if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "build")):
                tar_items.append(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "build"))
            if os.path.exists(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "patch")):
                tar_items.append(os.path.join(SourceStream.DIR_BUILTSCRIPTS, package_name, package_version, "patch"))
        else:
            logger.log.warn(f"The package {package_name} does not have a manifest.")

        # Create tar file
        tar_output_path = os.path.join(SourceStream.DIR_OUTPUT, package_name, f"{package_fullname}.tar.xz")
        subprocess.run(["tar", "-cJf", tar_output_path, "-C", SourceStream.DIR_INPUT] + tar_items, check=True)

        # Cleanup the input folder
        shutil.rmtree(package_path_folder)

        logger.log.ok(f"Repacked package \x1b[1;37m{package_name}({package_version})\x1b[0m Successfully.")
    except Exception as e:
        logger.log.fail(f"Error trying to repack package \x1b[1;37m{package_name}({package_version})\x1b[0m, Configuration error?\n{e}")