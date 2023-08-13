from .. import SourceStream;

from ..vendor.SplashPyUtils import logger, text
from ..file import download, repack, config
from .help import help

import requests
import yaml
import sys
import dload
import os

YAML_CONFIG = {}
YAML_EDITION = {}
YAML_SOURCES = {}

PACKAGES = [];
PACKAGES_ALL = False;

def run_command():
    global YAML_CONFIG, YAML_EDITION, YAML_SOURCES, PACKAGES;
    YAML_CONFIG, YAML_EDITION, YAML_SOURCES = config.load()


    for arg in sys.argv[1:]:
        arg = arg.lower().split(":")

        if arg[0] in ["--help", "--man", "--manual"]:
            run_command_help()

        if arg[0] in ["--package", "--p"]:
            run_command_package(arg);
    

    

    # Print basic tool information
    text_title = text.format("\x1b[1;36mSourceStream\x1b[1;0m");
    text_title.center();

    text_desc = text.format("\x1b[0;36mA tool to download, patch and repack core packages for SplashOS\x1b[1;0m");
    text_desc.center();
    
    text_ver = text.format("\x1b[0;36mVersion: " + SourceStream.VERSION_STR +" (" + SourceStream.VERSION_DATE + ")\x1b[0;0m");
    text_ver.center();

    logger.log.info(SourceStream.separator);
    logger.log.info("");
    logger.log.info(text_title.ret())
    logger.log.info(text_desc.ret())
    logger.log.info(text_ver.ret())
    logger.log.info("")
    logger.log.info(SourceStream.separator);
    logger.log.print("\n");



    # Create input/output directory
    logger.log.info("Created input/output directory's.");
    os.makedirs(SourceStream.DIR_INPUT, exist_ok=True)
    os.makedirs(SourceStream.DIR_OUTPUT, exist_ok=True)
    
    print(SourceStream.DIR_BUILTSCRIPTS)


    # Cloning buildscipt repo
    logger.log.info("Cloning buildscript repository.");
    if not os.path.exists(SourceStream.DIR_BUILTSCRIPTS):
        dload.git_clone("https://github.com/MVDW-SplashOS/BuildScripts.git", SourceStream.DIR_BUILTSCRIPTS);


    if len(PACKAGES) == 0 and PACKAGES_ALL == False:
        logger.log.fail("No packages to repack.");
        exit(1);


    if PACKAGES_ALL:
        tools = YAML_EDITION["packages"]
    else:
        tools = PACKAGES;

    logger.log.info("Starting to download and check packages, this can take a while...");
    for tool in tools:
        download.download_tool(tool, YAML_SOURCES)

    logger.log.info("Starting to repack packages, this can take a while...");
    for tool in tools:
        repack.repack_tool(tool, YAML_SOURCES)


    logger.log.print("");

    logger.log.info(SourceStream.separator);
    logger.log.info("");
    logger.log.info("Finished repacking.");
    logger.log.info("");




def run_command_help():
    help.print_help()
    exit()

def run_command_package(arg):
    global PACKAGES, PACKAGES_ALL, YAML_EDITION

    if 2 <= len(arg) <= 3:

        if len(arg) == 2:
            found = False
            if arg[1] == "all":

                PACKAGES_ALL = True;
                return;

            for tool in YAML_EDITION["packages"]:
                if tool["package"] == arg[1]:
                    package_info = {"package": arg[1], "version": tool["version"]}
                    found = True
                    break;
            if not found:
                logger.log.fail("Can't find the package '" + arg[1] + "', did you spell the name correctly?");
                exit(1);
        elif len(arg) == 3:
            package_info = {"package": arg[1], "version": arg[2]}

        PACKAGES.append(package_info)

    else:
        logger.log.fail("Invalid package argument: --package:<package>:[version]")
        exit(1)