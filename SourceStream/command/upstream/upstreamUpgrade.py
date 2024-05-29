from ... import SourceStream;

from ...vendor.SplashPyUtils import logger

from . import upstreamAdd, upstreamModify, upstreamChecksum, upstreamRemove



def run(arg):
    
    if len(arg) < 2 or len(arg) > 3:
        logger.log.fail("Invalid upstream upgrade argument: --upstream-upgrade:<edition>:[package]")
        exit(1)

    if len(arg) < 3 or arg[2] == "all":
        SourceStream.PACKAGES_ALL = True

    if arg[1] not in SourceStream.EDITION_LIST:
        logger.log.fail("Selected edition is not valid.")
        exit(1)
    
    SourceStream.EDITION_SELECTED = arg[1]