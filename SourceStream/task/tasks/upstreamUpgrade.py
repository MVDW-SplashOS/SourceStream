from ...vendor.SplashPyUtils import logger

import ruamel.yaml
import requests
import json
import sys
from bs4 import BeautifulSoup as BS

def get_package_info()->list:
    
    url = 'https://www.linuxfromscratch.org/lfs/view/stable-systemd/chapter03/packages.html'
    response = requests.get(url)
    
    if response.status_code != 200:
        # add log here
        return None
    
    soup = BS(response.text, 'html.parser')
    packages = soup.find_all('span', {'class':'term'})
    packages_list = []
    
    for i in packages:
        text = i.text
        
        package_name = text.split('(')[0].strip()
        package_version = text.split('(')[1].split(')')[0]
        package = [package_name, package_version]
        
        packages_list.append(package)
        
    return packages_list


def get_package_mapping(file):
    with open(file) as json_data:
        return json.load(json_data)



def check_mapping(packages, mapping):
    success = True
    for package in packages:
        if not mapping.get(package[0]):
            logger.log.fail(f"Package {package[0]} has no mapping.")
            success = False

    return success



def run():
    logger.log.info("Getting package and edition data...")

    packages = get_package_info()
    packages_mapped = []
    mapping = get_package_mapping("input/LFS-mapping.json")


    if not check_mapping(packages, mapping):
        print("Not all packages are mapped, exiting...")
        logger.log.fail("Not all packages are mapped.")
        exit(1)
    
    logger.log.info("Validated edition mappings")

    # After validating remapping every package
    for package in packages:
        packages_mapped.append([mapping.get(package[0]), package[1]])
    
    with open("./edition-configuration.yml", "r") as edition_raw:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        edition = yaml.load(edition_raw)


    for i in range(len(edition["packages"])):
        new_version = 0

        for package_map in packages_mapped: 
            if package_map[0] == edition["packages"][i]["package"]:
                new_version = package_map[1]

        edition["packages"][i]["version"] = new_version

    logger.log.info("Upading done, writing...")

    with open("./edition-configuration.yml", "w") as edition_raw:
        yaml.dump(edition, edition_raw)

