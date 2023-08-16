from .vendor.SplashPyUtils import logger, text
from .command import commandManager
from .file import config, download, repack, push

import dload
import sys
import os

# Versioning
VERSION_STR = "2.1.0";
VERSION_DATE = "13 Aug 2023";

# Download retry unused for now because md5sum are not included with upstream-sources.yml yet.
DOWNLOAD_RETRYS = 0;
DOWNLOAD_RETRYS_MAX = 3;

# separator
separator = "--------------------------------------------------------------------";

# Paths
DIR_CURRENT = os.path.dirname(os.path.abspath(sys.argv[0]))
DIR_INPUT = DIR_CURRENT + "/input/";
DIR_OUTPUT = DIR_CURRENT + "/output/";
DIR_BUILTSCRIPTS = DIR_INPUT + "BuildScripts-main/";

# All yaml files
YAML_CONFIG = {}
YAML_EDITION = {}
YAML_SOURCES = {}

# Package information
PACKAGES = [];
PACKAGES_ALL = False;

def main():
    global YAML_CONFIG, YAML_EDITION, YAML_SOURCES, PACKAGES;

    if len(sys.argv) == 1:
        logger.log.warn("Usage: 'python3 " + sys.argv[0] + " --<argument 1> --[argument 2]'");
        logger.log.print("");
        logger.log.print("For the manual please add the --help argument.");
        return;

    YAML_CONFIG, YAML_EDITION, YAML_SOURCES = config.load()

    commandManager.run_command()


    # Print basic tool information
    text_title = text.format("\x1b[1;36mSourceStream\x1b[1;0m");
    text_title.center();

    text_desc = text.format("\x1b[0;36mA tool to download, patch and repack core packages for SplashOS\x1b[1;0m");
    text_desc.center();
    
    text_ver = text.format("\x1b[0;36mVersion: " + VERSION_STR +" (" + VERSION_DATE + ")\x1b[0;0m");
    text_ver.center();

    logger.log.info(separator);
    logger.log.info("");
    logger.log.info(text_title.ret())
    logger.log.info(text_desc.ret())
    logger.log.info(text_ver.ret())
    logger.log.info("")
    logger.log.info(separator);
    logger.log.print("\n");


    # Create input/output directory
    logger.log.info("Created input/output directory's.");
    os.makedirs(DIR_INPUT, exist_ok=True)
    os.makedirs(DIR_OUTPUT, exist_ok=True)


    # Cloning buildscipt repo
    logger.log.info("Cloning buildscript repository.");
    if not os.path.exists(DIR_BUILTSCRIPTS):
        dload.git_clone("https://github.com/MVDW-SplashOS/BuildScripts.git", DIR_INPUT);


    if len(PACKAGES) == 0 and PACKAGES_ALL == False:
        logger.log.fail("No packages to repack.");
        exit(1);


    if PACKAGES_ALL:
        tools = YAML_EDITION["packages"]
    else:
        tools = PACKAGES;

    logger.log.info("Starting to download and check packages, this can take a while...");
    for tool in tools:
        download.download_tool(tool)

    logger.log.info("Starting to repack packages, this can take a while...");
    for tool in tools:
        repack.repack_tool(tool)

    logger.log.info("Starting to push packages to final destination...");
    push.push(tools)

    logger.log.print("");

    logger.log.info(separator);
    logger.log.info("");
    logger.log.info("Finished repacking.");
    logger.log.info("");