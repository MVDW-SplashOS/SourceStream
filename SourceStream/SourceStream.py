from .vendor.SplashPyUtils import logger, text, config
from .command import commandManager

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

DIR_CURRENT = os.path.dirname(os.path.abspath(sys.argv[0]))
DIR_INPUT = DIR_CURRENT + "/input/";
DIR_OUTPUT = DIR_CURRENT + "/output/";
DIR_BUILTSCRIPTS = DIR_INPUT + "BuildScripts";


def main():

    if len(sys.argv) == 1:
        logger.log.warn("Usage: 'python3 " + sys.argv[0] + " --<argument 1> --[argument 2]'");
        logger.log.print("");
        logger.log.print("For the manual please add the --help argument.");
        return;

    commandManager.run_command()
