from ... import SourceStream;

from ...vendor.SplashPyUtils import logger

from . import upstreamAdd, upstreamModify, upstreamChecksum, upstreamRemove


def run(command, arg):
    delimiter = '-'
    command_full = delimiter.join(command)

    if command_full in ["upstream-add"]:
        upstreamAdd.run(arg)

    elif command_full in ["upstream-modify"]:
        upstreamModify.run(arg)

    elif command_full in ["upstream-checksum"]:
        upstreamChecksum.run(arg)

    elif command_full in ["upstream-remove"]:
        upstreamRemove.run(arg)

    else:
        logger.log.fail("Invalid upstream argument, please check the manual: --help")
        exit(1)
