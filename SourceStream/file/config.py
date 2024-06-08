from .. import SourceStream
from ..vendor.SplashPyUtils import config, logger

import requests
import os

# Loads all config files and download extra config files when needed
def load():
    YAML_CONFIG = config.configloader("config").load()

    # Create input/output directory
    logger.log.info("Created input/output directory's.")
    os.makedirs(SourceStream.DIR_INPUT, exist_ok=True)
    os.makedirs(SourceStream.DIR_OUTPUT, exist_ok=True)


    if not os.path.isfile("input/LFS-mapping.json"):
        r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/LFS-mapping.json")
        open("input/LFS-mapping.json", 'wb').write(r.content)


    if YAML_CONFIG["update-sources"] and not os.path.isfile(".lock-sources"):
        r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/upstream-sources.yml")
        open("upstream-sources.yml", 'wb').write(r.content)
    YAML_SOURCES = config.configloader("sources").load()

    if YAML_CONFIG["edition"] != "custom" or YAML_CONFIG["update-edition"]:
        r = requests.get(f"https://www.enthix.net/SplashOS/downloads/configs/edition-packages/{YAML_CONFIG["version"]}/{YAML_CONFIG["edition"]}.yml")
        open("edition-configuration.yml", 'wb').write(r.content)
    YAML_EDITION = config.configloader("edition").load()

    return YAML_CONFIG, YAML_EDITION, YAML_SOURCES
