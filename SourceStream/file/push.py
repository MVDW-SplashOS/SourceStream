from .. import SourceStream

from ..vendor.SplashPyUtils import logger

import paramiko
import os

def push(packages):
    if SourceStream.YAML_CONFIG["push"]["type"] == "sftp":
        push_sftp(packages)
    elif SourceStream.YAML_CONFIG["push"]["type"] == "none":
        logger.log.info("No push type set, will not move package from output.")
    else:
        logger.log.fail(f"Invalid push type '{SourceStream.YAML_CONFIG["push"]["type"]}' in configuration.")
        exit(1)

def push_sftp(packages):
    
    sftp_host = SourceStream.YAML_CONFIG["push"]["sftp"]["host"]
    sftp_port = SourceStream.YAML_CONFIG["push"]["sftp"]["port"]
    sftp_username = SourceStream.YAML_CONFIG["push"]["sftp"]["username"]
    sftp_password = SourceStream.YAML_CONFIG["push"]["sftp"]["password"]
    sftp_path = SourceStream.YAML_CONFIG["push"]["sftp"]["path"]

    for package in packages:

        package_name = package["package"]
        package_version = package["version"]
        package_file =  f"{package_name}-{package_version}.tar.xz"

        with paramiko.SSHClient() as ssh:
            try:


                ssh.load_system_host_keys()
                ssh.connect(sftp_host, username=sftp_username, password=sftp_password, port=sftp_port, look_for_keys=False, allow_agent=False)
            
                sftp = ssh.open_sftp()
                logger.log.info(f"Connected to '{sftp_host}:{sftp_port}'")

                
                local_file = os.path.join(SourceStream.DIR_OUTPUT, package_name, package_file)
                remote_path = os.path.join(sftp_path, package_name)
                remote_file = os.path.join(remote_path, package_file)

                try:
                    sftp.chdir(remote_path)
                except IOError:
                    logger.log.info("Package does not exist on remote, creating directory.")
                    sftp.mkdir(remote_path)
                    sftp.chdir(remote_path)
                

                
                sftp.put(local_file, remote_file)

            except paramiko.ssh_exception.NoValidConnectionsError:
                logger.log.fail(f"Failed to connect to '{sftp_host}:{sftp_port}'")
                exit(1)
            except paramiko.ssh_exception.SSHException:
                logger.log.fail("An unknown error occurred while connecting")
                exit(1)
            except FileNotFoundError:
                logger.log.fail(f"The path '{sftp_path}' does not exist.")
                
                exit(1)
            except OSError:
                logger.log.fail("An unknown error occurred while transfering data, please check if permissions are set correctly.")