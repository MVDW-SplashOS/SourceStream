from .. import SourceStream

from ..vendor.SplashPyUtils import logger

import asyncio
import aiohttp
import time
import os

async def download_tool(packages):
    
    package_list = []
    
    for package in packages:
        package_name = package["package"]
        package_version = package["version"]
        package_version_split = package["version"].split(".")

        package_url = SourceStream.YAML_SOURCES[package_name]["url"].replace("{VERSION}", package_version)
        package_url = package_url.replace("{VERSION_SEPARATE_UNDERSCORE}", package_version.replace(".", "_"))

        if(len(package_version_split) >= 1): package_url = package_url.replace("{VERSION_MAJOR}", package_version_split[0])
        if(len(package_version_split) >= 2): package_url = package_url.replace("{VERSION_MINOR}", package_version_split[1])
        if(len(package_version_split) >= 3): package_url = package_url.replace("{VERSION_REVISION}", package_version_split[2])
        if(len(package_version_split) >= 4): package_url = package_url.replace("{VERSION_BUILD}", package_version_split[3])

        package_filename = os.path.basename(package_url)
        package_path = os.path.join(SourceStream.DIR_INPUT, package_filename)
        
        if not os.path.exists(package_path):
            package_list.append({"name": package_name, "version": package_version, "url": package_url, "path": package_path})
        else:
            logger.log.ok(f"Package \x1b[1;37m{package_name}({package_version})\x1b[0m already downloaded.")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for package in package_list:
            tasks.append(download_package(session, package))
        
        await asyncio.gather(*tasks)
        
async def download_package(session, package):
    async with session.get(package["url"]) as response:
        if response.status == 200:
            with open(package["path"], 'wb') as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f_handle.write(chunk)
            logger.log.ok(f"Downloaded package \x1b[1;37m{package['name']}({package['version']})\x1b[0m Successfully.")
        else:
            logger.log.fail(f"Failed to download package \x1b[1;37m{package['name']}({package['version']})\x1b[0m.")
            logger.log.fail(f"Status code: {response.status}")

