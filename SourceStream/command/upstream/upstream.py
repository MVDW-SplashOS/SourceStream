from ... import SourceStream;

from ...vendor.SplashPyUtils import logger

from . import upstreamAdd, upstreamModify, upstreamChecksum, upstreamRemove, upstreamUpgrade


def run(command, arg):
    delimiter = '-'
    command_full = delimiter.join(command)

    if command_full in ["upstream-add"]:
        SourceStream.TASK_TYPES_ENABLED["UPSTREAM_ADD"] = True;
        upstreamAdd.run(arg)

    elif command_full in ["upstream-modify"]:
        SourceStream.TASK_TYPES_ENABLED["UPSTREAM_MODIFY"] = True;
        upstreamModify.run(arg)

    elif command_full in ["upstream-checksum"]:
        SourceStream.TASK_TYPES_ENABLED["UPSTREAM_CHECKSUM"] = True;
        upstreamChecksum.run(arg)

    elif command_full in ["upstream-remove"]:
        SourceStream.TASK_TYPES_ENABLED["UPSTREAM_REMOVE"] = True;
        upstreamRemove.run(arg)

    elif command_full in ["upstream-upgrade"]:
        SourceStream.TASK_TYPES_ENABLED["UPSTREAM_UPGRADE"] = True;
        upstreamUpgrade.run(arg)
        
    else:
        logger.log.fail("Invalid upstream argument, please check the manual: --help")
        exit(1)
