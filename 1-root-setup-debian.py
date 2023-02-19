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
    pass

def envvar():
    # set up environment variables
    shutilcopy('environment', '/etc/')
    chmod('/etc/environment',0o644)

def user():
    # modify user
    groups = "sudo,data"
    bash(f'/usr/sbin/usermod -a -G {groups} {user}')		
    # get hash via $ mkpasswd -m sha512crypt mypassword
    epwd = '$6$djg0mn/uDqZkGIFH$nizpdm1cChbWrMd2aNU3cRE6XeQOUu1gigMCPL/BnjJl1gbO9rgxn3EtKkPRx3Im6V/.oMG5TWGGcqgghRiwy0'
    epwd = bytes(f'{user}:{epwd}', 'utf-8')
    bash('/usr/sbin/chpasswd --encrypted', input=epwd)

def grub():
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
    update()
    hostname()
    networkinterface()
    envvar()
    user()
    grub()
    return 0

if __name__ == "__main__":
    exit(main(argv[1:]))
