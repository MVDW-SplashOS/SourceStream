from ... import SourceStream;

from ...vendor.SplashPyUtils import logger


def add(arg):
    if len(arg) < 2 or len(arg) > 3:
        logger.log.fail("Invalid package argument: --package:<package>:[version]")
        exit(1)

    if len(arg) == 2 and arg[1] == "all":
        SourceStream.PACKAGES_ALL = True
        return

    package_info = None

    for tool in SourceStream.YAML_EDITION["packages"]:
        if tool["package"] == arg[1]:
            if len(arg) == 3:
                package_info = {"package": arg[1], "version": arg[2]}  
            else:
                package_info = {"package": arg[1], "version": tool["version"]}
            break
    if package_info is None:
        logger.log.fail(f"Can't find the package '{arg[1]}', did you spell the name correctly?")
        exit(1)
    

    SourceStream.PACKAGES.append(package_info)