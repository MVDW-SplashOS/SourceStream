from ..vendor.SplashPyUtils import logger

import requests
import os

def download_tools_list(yaml_edition, yaml_sources):
    for tool in yaml_edition["packages"]:

        package = tool["package"];
        version = tool["version"];
        url = yaml_sources[package]["url"].replace("{VERSION}", version);
        filename = os.path.basename(url);

        if not os.path.exists(DIR_INPUT + filename):
            r = requests.get(url)
            open(DIR_INPUT + filename, 'wb').write(r.content)
            logger.log.ok("Downloaded package \x1b[1;37m" + package + "\x1b[0m Successfully.")

