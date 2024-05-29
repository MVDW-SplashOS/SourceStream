from .vendor.SplashPyUtils import logger, text

from .command import commandManager
from .task import taskManager
from .file import config

import dload
import sys
import os

# Versioning
VERSION_STR = "2.2.0";
VERSION_DATE = "18 May 2024";

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

# Tasks types enabled
TASK_TYPES_ENABLED = {
    "REPACK_PACKAGES": False,
    "UPSTREAM_UPGRADE": False
}

# Package information
PACKAGES = [];
PACKAGES_ALL = False;
PACKAGE_REBUILD_AFTEER_BUILD = False;
PACKAGE_REBUILDING = False;

# Edition information
EDITION_LIST = ["molecule"] # Todo: make it a configuration fike
EDITION_SELECTED = None;

# Running as service
AS_SERVICE = False;

def main():
    global YAML_CONFIG, YAML_EDITION, YAML_SOURCES, PACKAGES;

    if len(sys.argv) == 1:
        logger.log.warn("Usage: 'python3 " + sys.argv[0] + " --<argument 1> --[argument 2]'");
        logger.log.print("");
        logger.log.print("For the manual please add the --help argument.");
        return;

    YAML_CONFIG, YAML_EDITION, YAML_SOURCES = config.load()

    commandManager.run()


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

    taskManager.run()

    logger.log.print("");

    logger.log.info(separator);
    logger.log.info("");
    logger.log.info("Finished all tasks.");
    logger.log.info("");