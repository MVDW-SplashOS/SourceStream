from ... import SourceStream;

from ...vendor.SplashPyUtils import logger, text

from ...file import download, repack, push

import dload
import sys
import os

def run():
    # Create input/output directory
    logger.log.info("Created input/output directory's.");
    os.makedirs(SourceStream.DIR_INPUT, exist_ok=True)
    os.makedirs(SourceStream.DIR_OUTPUT, exist_ok=True)


    # Cloning buildscipt repo
    logger.log.info("Cloning buildscript repository.");
    if not os.path.exists(SourceStream.DIR_BUILTSCRIPTS):
        dload.git_clone("https://github.com/MVDW-SplashOS/BuildScripts.git", SourceStream.DIR_INPUT);


    if len(SourceStream.PACKAGES) == 0 and SourceStream.PACKAGES_ALL == False:
        logger.log.fail("No packages to repack.");
        exit(1);


    if SourceStream.PACKAGES_ALL:
        tools = SourceStream.YAML_EDITION["packages"]
    else:
        tools = SourceStream.PACKAGES;

    logger.log.info("Starting to download and check packages, this can take a while...");
    for tool in tools:
        download.download_tool(tool)

    logger.log.info("Starting to repack packages, this can take a while...");
    for tool in tools:
        repack.repack_tool(tool)

    logger.log.info("Starting to push packages to final destination...");
    push.push(tools)