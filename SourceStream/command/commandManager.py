from .help import help
from ..vendor.SplashPyUtils import logger

import yaml
import sys

YAML_CONFIG = {};
YAML_EDITION = {};
YAML_SOURCES = {};

def run_command():

    packages = [];

    i=0;
    for arg in sys.argv:
        if i >= 1:
            arg = arg.lower().split(":");
            match arg[0]:
                case "--help" | "--man" | "--manual":
                    help.print_help();
                    return;
                case "--package" | "--p":
                    if len(arg) == 1:
                        logger.log.fail("The package argument requires one and one optional parameter: --package:<package>:[version]")
                        return;
                    elif len(arg) == 2:
                        package = []
                        package.append(arg[1]);
                        packages.append(package);
                    elif len(arg) == 3:
                        package = []
                        package.append(arg[1]);
                        package.append(arg[2]);
                        packages.append(package);
                    else:
                        logger.log.fail("Too many parameters for the package argument: --package:<package>:[version]");
                        return;

        i=i+1;
    
    print(packages)