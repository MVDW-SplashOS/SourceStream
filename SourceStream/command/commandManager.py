from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import sys

# Commands
from .help import help
from .package import package
from .package_list import package_list



def run_command():

    for arg in sys.argv[1:]:
        arg = arg.lower().split(":")

        if arg[0] in ["--help", "--man", "--manual"]:
            help.print_help()

        elif arg[0] in ["--package", "--p"]:
            package.run(arg);

        elif arg[0] in ["--package-list", "--list"]:
            package_list.run();
    
        else:
            logger.log.fail("Invalid argument, please check the manual: --help")
            exit(1)
    

