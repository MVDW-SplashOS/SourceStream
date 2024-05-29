from ... import SourceStream;

from ...vendor.SplashPyUtils import logger

from . import packageList, packageQueue


def run(command, arg):
    delimiter = '-'
    command_full = delimiter.join(command)

    if command_full in ["package", "p"]:
        packageQueue.add(arg)

    elif command_full in ["package-list", "list"]:
        packageList.show(arg)
        
    else:
        logger.log.fail("Invalid package argument, please check the manual: --help")
        exit(1)
