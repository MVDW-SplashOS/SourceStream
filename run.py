import requests
import tarfile
import shutil
import yaml
import sys
import git
import io
import os

VERSION_STR = "2.0.0";
VERSION_DATE = "10 Aug 2023";

# Download retry unused for now because md5sum are not included with upstream-sources.yml yet.
DOWNLOAD_RETRYS = 0;
DOWNLOAD_RETRYS_MAX = 3;

separator="--------------------------------------------------------------------";

YAML_CONFIG = {};
YAML_EDITION = {};
YAML_SOURCES = {};

class log:

    def info(message):
        sys.stderr.write("[INFO] " + message + "\n");

    def ok(message):
        sys.stderr.write("[ \x1b[0;32mOK\x1b[1;0m ] " + message + "\n");

    def warn(message):
        sys.stderr.write("[\x1b[0;93mWARN\x1b[1;0m] " + message + "\n");

    def fail(message):
        sys.stderr.write("[\x1b[1;31mFAIL\x1b[1;0m] " + message + "\n");


def configloader(file_type):
    mapping = {
        "config": ("config.yml", YAML_CONFIG),
        "edition": ("edition-configuration.yml", YAML_EDITION),
        "sources": ("upstream-sources.yml", YAML_SOURCES)
    }

    if file_type in mapping:
        file, data = mapping[file_type]
        with open(file, 'r') as stream:
            data.update(yaml.safe_load(stream))  # Update the dictionary with loaded content
    else:
        raise ValueError("Invalid file_type")



def download_tools_list():
    for tool in YAML_EDITION["packages"]:

        package = tool["package"];
        version = tool["version"];
        url = YAML_SOURCES[package]["url"].replace("{VERSION}", version);
        filename = os.path.basename(url);

        if not os.path.exists("./input/" + filename):
            r = requests.get(url)
            open("./input/" + filename, 'wb').write(r.content)
            log.ok("Downloaded package \x1b[1;37m" + package + "\x1b[0m Successfully.")

def repack_tool_list():
    for tool in YAML_EDITION["packages"]:
        package = tool["package"];
        version = tool["version"];
        url = YAML_SOURCES[package]["url"].replace("{VERSION}", version);
        filename = os.path.basename(url);
        

        with tarfile.open("./input/" + filename) as f:
            if not YAML_SOURCES[package]["subdir"]:
                os.makedirs("./input/" + package + "-" + version, exist_ok=True)
                f.extractall("./input/" + package + "-" + version)
            else:
                f.extractall("./input")

        if isinstance(YAML_SOURCES[package]["subdir"], str):
            subdir = YAML_SOURCES[package]["subdir"].replace("{VERSION}", version).replace("{PACKAGE}", package);
            os.rename("./input/" + subdir, "./input/" + package + "-" + version); 

        os.makedirs("./output/" + package, exist_ok=True)
        with tarfile.open("./output/" + package + "/" + package + "-" + version + ".tar.xz", "w:xz") as tar:
            tar.add("./input/" + package + "-" + version, arcname=package + "-" + version)

            # Check if buildscript exist for these packages
            if os.path.exists("./input/BuildScripts/" + package):
                tar.add("./input/BuildScripts/" + package + "/manifest.yml", arcname="manifest.yml")

                # Check if there are some extra folders included 
                if os.path.exists("./input/BuildScripts/" + package + "/build"):
                    tar.add("./input/BuildScripts/" + package + "/build", arcname="build")
                if os.path.exists("./input/BuildScripts/" + package + "/patch"):
                    tar.add("./input/BuildScripts/" + package + "/patch", arcname="patch")
            else:
                log.warn("The package " + package + " does not have a manifest.")

        shutil.rmtree("./input/" + package + "-" + version)
        log.ok("Repacked package \x1b[1;37m" + package + "\x1b[0m Successfully.")


def main():

    # Print basic tool information
    sys.stderr.write(separator);
    sys.stderr.write("\n\n");
    sys.stderr.write("\x1b[1;36mSourceStream\n")
    sys.stderr.write("\x1b[0;36mA tool to download, patch and repack core packages for SplashOS\n")
    sys.stderr.write("Version: " + VERSION_STR +" (" + VERSION_DATE + ")\x1b[0;0m\n")
    sys.stderr.write("\n")
    sys.stderr.write(separator);
    sys.stderr.write("\n\n");

    # Create input/output directory
    log.info("Created input/output directory's.");
    os.makedirs("./input", exist_ok=True)
    os.makedirs("./output", exist_ok=True)
    
    # Read config
    log.info("Reading config file.");
    configloader("config")

    # Downloading and reading latest source file
    log.info("Downloading latest source file");
    r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/upstream-sources.yml")
    open("upstream-sources.yml", 'wb').write(r.content)
    configloader("sources")

    # Downloading and reading edition configuration when needed, else check config
    if YAML_CONFIG["edition"] == "custom":
        log.info("Using custom edition, Checking if file is valid.");
        # TODO: Check if config is valid
    else:
        log.info("Get source file from " + YAML_CONFIG["edition"] + " edition.");
        r = requests.get("https://www.enthix.net/SplashOS/downloads/configs/edition-packages/" + YAML_CONFIG["version"] + "/" + YAML_CONFIG["edition"] + ".yml")
        open("edition-configuration.yml", 'wb').write(r.content)
    configloader("edition")

    # Cloning buildscipt repo
    log.info("Cloning buildscript repository.");
    if not os.path.exists("./input/BuildScripts"):
        git.Git("./input").clone("https://github.com/MVDW-SplashOS/BuildScripts.git");
    
    # Downloading all required packages
    log.info("Starting to download and check packages, this can take a while...");
    download_tools_list()
    log.info("Downloading and checking packages has been complete.");

    log.info("Starting to repack packages, this can take a while...");
    repack_tool_list();
    log.info("Repacking tools has been complete.");

    sys.stderr.write(separator);
    sys.stderr.write("\n");
    sys.stderr.write("Finished repacking.");
    sys.stderr.write("\n");

if __name__=="__main__":
    main()