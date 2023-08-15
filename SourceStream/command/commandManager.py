from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import sys

# Commands
from .help import help
from .package import package
from .upstream import upstream



def run_command():

    for arg in sys.argv[1:]:

        arg = arg.split(":")
        command = arg[0].replace("--", "").split("-")
        

        if command[0] in ["help", "man", "manual"]:
            help.print_help()

        elif command[0] in ["package", "p", "list"]:
            package.run(command, arg);

        elif command[0] in ["upstream"]:
            upstream.run(command, arg);
    
        else:
            logger.log.fail("Invalid argument, please check the manual: --help")
            exit(1)
    

