
def repack_tool_list():
    for tool in YAML_EDITION["packages"]:
        package = tool["package"];
        version = tool["version"];
        url = YAML_SOURCES[package]["url"].replace("{VERSION}", version);
        filename = os.path.basename(url);
        

        with tarfile.open(DIR_INPUT + filename) as f:
            if not YAML_SOURCES[package]["subdir"]:
                os.makedirs(DIR_INPUT + package + "-" + version, exist_ok=True)
                f.extractall(DIR_INPUT + package + "-" + version)
            else:
                f.extractall(DIR_INPUT)

        if isinstance(YAML_SOURCES[package]["subdir"], str):
            subdir = YAML_SOURCES[package]["subdir"].replace("{VERSION}", version).replace("{PACKAGE}", package);
            os.rename(DIR_INPUT + subdir, DIR_INPUT + package + "-" + version); 

        os.makedirs(DIR_OUTPUT + package, exist_ok=True)
        with tarfile.open(DIR_OUTPUT + package + "/" + package + "-" + version + ".tar.xz", "w:xz") as tar:
            tar.add(DIR_INPUT + package + "-" + version, arcname=package + "-" + version)

            # Check if buildscript exist for these packages
            if os.path.exists(DIR_BUILTSCRIPTS + package):
                tar.add(DIR_BUILTSCRIPTS + package + "/manifest.yml", arcname="manifest.yml")

                # Check if there are some extra folders included 
                if os.path.exists(DIR_BUILTSCRIPTS + package + "/build"):
                    tar.add(DIR_BUILTSCRIPTS + package + "/build", arcname="build")
                if os.path.exists(DIR_BUILTSCRIPTS + package + "/patch"):
                    tar.add(DIR_BUILTSCRIPTS + package + "/patch", arcname="patch")
            else:
                logger.log.warn("The package " + package + " does not have a manifest.")

        shutil.rmtree(DIR_INPUT + package + "-" + version)
        logger.log.ok("Repacked package \x1b[1;37m" + package + "\x1b[0m Successfully.")