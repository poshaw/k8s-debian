#! /usr/bin/env python
# coding: utf-8

"""
    This script sets up a fresh debian install to a known configuration

    Warning: unless you are me, don't run this script.

    You at a minimum need to change "user" to your user name, and "epwd" to your
    hashed-password
"""

from getpass import getpass
from myutils import bash
from os import chmod
import psutil
from pwd import getpwname
from shutil import copy as shutilcopy
from subprocess import PIPE
from sys import exit, argv

user = 'phil'

try:
    getpwname(user)
except KeyError:
    # TODO create user
    pass

def update():
    """
    Updates the package list and upgrades all installed packages to their latest versions.

    This function uses the 'apt' package manager to update the system. It first updates the package
    list by downloading the latest package information from the software repositories. Then, it
    upgrades all currently installed packages to their latest versions. The '-y' flag is used to
    automatically answer 'yes' to all prompts.

    This function installs some commonly used packages such as 'sudo', 'htop', 'git', 'python3-pip',
    'psmisc', 'neovim', 'curl', and 'openssh-server'. You can customize the list of packages to
    install by modifying the 'bash' command inside this function.

    Note that this function requires superuser privileges to run, so it should be executed as a
    privileged user or with the 'sudo' command.

    Raises:
        subprocess.CalledProcessError: If the 'apt' command fails or returns a non-zero exit status.
    """
    # implementation here

    bash('/usr/bin/apt update')		
    bash('/usr/bin/apt upgrade -y')		

    # install packages
    bash('/usr/bin/apt install -y sudo htop git python3-pip psmisc neovim curl openssh-server')		

def hostname():
    """
    Configures the hostname and IP address for the local machine by modifying the
    '/etc/hostname' and '/etc/hosts' files.

    This function sets the hostname of the machine by writing the first hostname-IP
    pair from the 'computers' list to the '/etc/hostname' file. It then sets up the
    IP address mappings for all machines in the 'computers' list in the '/etc/hosts'
    file. 

    Note that this function assumes that the '/etc/hosts' file already exists and
    contains the default '127.0.0.1' loopback mapping.

    Parameters:
        None

    Returns:
        None
    """
    # implementation here

    computers = [("km1", "192.168.56.50"),
                 ("kw1", "192.168.56.60")]
    domain = "lan"
    with open('/etc/hostname', 'w') as file:
        file.write("computers[0][0]\n")

    with open('/etc/hosts', 'r') as file:
        text = file.readlines()

    for i, line in enumerate(text):
        if '127.0.1.1' in line:
            text[i] = f'127.0.1.1\t{computers[0][0]} {computers[0][0]}.{domain}\n'
            break

    text.append('\n')
    for computer in computers:
        text.appned(f'{computer[1]}\t{computer[0]} {computer[0]}.{domain}\n')

    with open('/etc/hosts', 'w') as file:
        file.writelines(text)

def networkinterface():
    
    def list_interfaces_without_ip():
        interfaces = psutil.net_if_addrs()
        result = []
        for interface in interfaces:
            if not any(addr.family == 2 for addr in interfaces[interface]):
                result.append(interface)
        return result
    
    interfaces_without_ip = list_interfaces_without_ip()
    print(interfaces_without_ip)


def envvar():
    """
    Sets up the environment variables for the system by copying the `environment` file to `/etc/` and setting its permissions
    to read-only. The `environment` file contains environment variables for the system, such as `PATH`, `LANG`, and `LC_ALL`. 
    These environment variables affect how programs run on the system and can be customized to suit specific needs. By default, 
    this function sets up the environment variables for the current user, but you can modify the `environment` file to set up 
    environment variables for all users on the system.

    Raises:
        FileNotFoundError: If the `environment` file does not exist in the current working directory.
        PermissionError: If the script does not have permission to copy the `environment` file to `/etc/` or to change its permissions.
    """
    # set up environment variables
    shutilcopy('environment', '/etc/')
    chmod('/etc/environment',0o644)

def user():
    """
    Modifies the user account by adding it to the 'sudo' and 'data' groups, and sets the user password.
    
    The 'sudo' group is necessary to grant the user superuser privileges, while the 'data' group is an example
    custom group that could be used for data-related operations. You can customize the list of groups by modifying
    the 'groups' variable inside this function.
    The user password is set by passing the hashed password to the 'chpasswd' command. The 'epwd' variable contains
    a sample hashed password for the user 'phil', which you should modify with your own hashed password before running
    the script. You can generate the hashed password using the 'mkpasswd' command on a Linux system.
    Note that this function requires superuser privileges to run, so it should be executed as a privileged user or
    with the 'sudo' command.
    """

    # modify user
    groups = "sudo,data"
    bash(f'/usr/sbin/usermod -a -G {groups} {user}')		
    # get hash via $ mkpasswd -m sha512crypt mypassword
    epwd = '$6$djg0mn/uDqZkGIFH$nizpdm1cChbWrMd2aNU3cRE6XeQOUu1gigMCPL/BnjJl1gbO9rgxn3EtKkPRx3Im6V/.oMG5TWGGcqgghRiwy0'
    epwd = bytes(f'{user}:{epwd}', 'utf-8')
    bash('/usr/sbin/chpasswd --encrypted', input=epwd)

def grub():
    """
    Configures the GRUB bootloader.
    
    This function modifies the configuration file for the GRUB bootloader to reduce the boot timeout
    from 5 seconds to 0 seconds, which will speed up the boot process. The 'update-grub' command is
    then used to update the GRUB configuration file based on the changes made.
    Note that this function requires superuser privileges to run, so it should be executed as a
    privileged user or with the 'sudo' command.
    Raises:
        subprocess.CalledProcessError: If the 'update-grub' command fails or returns a non-zero
        exit status.
    """

    # fix grub timeout
    with open('/etc/default/grub', 'r') as file:
        text = file.readlines()

    for i, line in enumerate(text):
        if 'GRUB_TIMEOUT' in line:
            text[i] = line.replace('5', '0')
            break

    with open('/etc/default/grub', 'w') as file:
        file.writelines(text)

    bash('/usr/sbin/update-grub')		

def main(args):
    def main(args):
    """
    Sets up a fresh Debian installation to a known configuration by executing several configuration
    tasks, such as updating the system, configuring the hostname, setting up environment variables,
    modifying the user, and fixing the GRUB timeout. This function takes no arguments, and returns 0
    upon successful completion.

    Args:
        args (list): A list of command-line arguments. This parameter is unused in this function.

    Returns:
        int: The exit code of the program. Returns 0 upon successful completion.
    """

    update()
    hostname()
    networkinterface()
    envvar()
    user()
    grub()
    return 0

if __name__ == "__main__":
    exit(main(argv[1:]))
