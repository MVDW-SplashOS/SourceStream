from ... import SourceStream

from ...vendor.SplashPyUtils import logger, text

from ...file import download, repack, push


import multiprocessing
import shutil
import dload
import sys
import os


def run():

    SourceStream.PACKAGE_REBUILDING = True

    # Create input/output directory
    logger.log.info("Created input/output directory's.")
    os.makedirs(SourceStream.DIR_INPUT, exist_ok=True)
    os.makedirs(SourceStream.DIR_OUTPUT, exist_ok=True)

    logger.log.info("Cleaning input directory when necessary.")
    for item in os.listdir(SourceStream.DIR_INPUT):
            item_path = os.path.join(SourceStream.DIR_INPUT, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)


    # Cloning buildscipt repo
    logger.log.info("Cloning buildscript repository.")
    if not os.path.exists(SourceStream.DIR_BUILTSCRIPTS):
        dload.git_clone("https://github.com/MVDW-SplashOS/BuildScripts.git", SourceStream.DIR_INPUT)


    if len(SourceStream.PACKAGES) == 0 and SourceStream.PACKAGES_ALL == False:
        logger.log.fail("No packages to repack.")
        if(SourceStream.AS_SERVICE):
            return
        else:
            exit(1)


    if SourceStream.PACKAGES_ALL:
        tools = SourceStream.YAML_EDITION["packages"]
    else:
        tools = SourceStream.PACKAGES

    logger.log.info("Starting to download and check packages, this can take a while...")
    for tool in tools:
        download.download_tool(tool)

    logger.log.info("Starting to repack packages, this can take a while...")
        
    # Repack packages with multiprocessing
    cores = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=cores) as pool:
        pool.map(repack.repack_tool, tools)
        
    logger.log.info("Starting to push packages to final destination...")
    push.push(tools)

    SourceStream.PACKAGE_REBUILDING = False
    if(SourceStream.AS_SERVICE and SourceStream.PACKAGE_REBUILD_AFTEER_BUILD):
        SourceStream.PACKAGE_REBUILD_AFTEER_BUILD = False
        run()