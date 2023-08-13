from .vendor.SplashPyUtils import logger, text, config
from .command import commandManager

import requests
import tarfile
import shutil
import yaml
import git
import sys
import io
import os

VERSION_STR = "2.0.0";
VERSION_DATE = "10 Aug 2023";

# Download retry unused for now because md5sum are not included with upstream-sources.yml yet.
DOWNLOAD_RETRYS = 0;
DOWNLOAD_RETRYS_MAX = 3;

separator="--------------------------------------------------------------------";

DIR_INPUT = "./input/";
DIR_OUTPUT = "./output/";
DIR_BUILTSCRIPTS = DIR_INPUT + "BuildScripts";


def main():
    global YAML_CONFIG, YAML_EDITION, YAML_SOURCES;

    if len(sys.argv) == 1:
        logger.log.warn("Usage: 'python3 " + sys.argv[0] + " --<argument 1> --[argument 2]'");
        logger.log.print("");
        logger.log.print("For the manual please add the --help argument.");
        return;

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
    


    # Read config
    logger.log.info("Reading config file.");
    YAML_CONFIG = config.configloader("config").load()



    # Downloading and reading latest source file
    logger.log.info("Downloading latest source file");
    r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/upstream-sources.yml")
    open("upstream-sources.yml", 'wb').write(r.content)
    YAML_SOURCES = config.configloader("sources").load()



    # Downloading and reading edition configuration when needed, else check config
    if YAML_CONFIG["edition"] == "custom":
        logger.log.info("Using custom edition, Checking if file is valid.");
        # TODO: Check if config is valid
    else:
        logger.log.info("Get source file from " + YAML_CONFIG["edition"] + " edition.");
        r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/edition-packages/" + YAML_CONFIG["version"] + "/" + YAML_CONFIG["edition"] + ".yml")
        open("edition-configuration.yml", 'wb').write(r.content)
    YAML_EDITION = config.configloader("edition").load();



    # Cloning buildscipt repo
    logger.log.info("Cloning buildscript repository.");
    if not os.path.exists(DIR_BUILTSCRIPTS):
        git.Git(DIR_BUILTSCRIPTS).clone("https://github.com/MVDW-SplashOS/BuildScripts.git");



    # Downloading all required packages
    logger.log.info("Starting to download and check packages, this can take a while...");
    download_tools_list()
    logger.log.info("Downloading and checking packages has been complete.");

    logger.log.info("Starting to repack packages, this can take a while...");
    repack_tool_list();
    logger.log.info("Repacking tools has been complete.");

    logger.log.print("");

    logger.log.info(separator);
    logger.log.info("");
    logger.log.info("Finished repacking.");
    logger.log.info("");


