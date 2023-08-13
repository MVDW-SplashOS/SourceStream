from .. import SourceStream;

from ..vendor.SplashPyUtils import logger

import requests
import os

def download_tool(tool, yaml_sources):
    package = tool["package"];
    version = tool["version"];
    url = yaml_sources[package]["url"].replace("{VERSION}", version);
    filename = os.path.basename(url);

    if not os.path.exists(SourceStream.DIR_INPUT + filename):
        r = requests.get(url)
        open(SourceStream.DIR_INPUT + filename, 'wb').write(r.content)
        logger.log.ok("Downloaded package \x1b[1;37m" + package + "\x1b[0m Successfully.")

