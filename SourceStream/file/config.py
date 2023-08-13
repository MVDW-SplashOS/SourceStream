from ..vendor.SplashPyUtils import config

import requests

# Loads all config files and download extra config files when needed
def load():
    YAML_CONFIG = config.configloader("config").load()

    r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/upstream-sources.yml")
    open("upstream-sources.yml", 'wb').write(r.content)
    YAML_SOURCES = config.configloader("sources").load()

    if YAML_CONFIG["edition"] != "custom":
        r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/edition-packages/" + YAML_CONFIG["version"] + "/" + YAML_CONFIG["edition"] + ".yml")
        open("edition-configuration.yml", 'wb').write(r.content)
    YAML_EDITION = config.configloader("edition").load();

    return YAML_CONFIG, YAML_EDITION, YAML_SOURCES
