from ... import SourceStream;

from ...vendor.SplashPyUtils import logger


def add(arg):
    if len(arg) < 2 or len(arg) > 3:
        logger.log.fail("Invalid package argument: --package:<package>:[version]")
        exit(1)

    if len(arg) == 2 and arg[1] == "all":
        SourceStream.PACKAGES_ALL = True
        return

    package_info = {"package": arg[1], "version": arg[2]} if len(arg) == 3 else None

    if package_info is None:
    
        for tool in SourceStream.YAML_EDITION["packages"]:
            if tool["package"] == arg[1]:
                package_info = {"package": arg[1], "version": tool["version"]}
                break
        else:
            logger.log.fail("Can't find the package '{arg[1]}', did you spell the name correctly?")
            exit(1)
        

    SourceStream.PACKAGES.append(package_info)