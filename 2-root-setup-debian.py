#! /usr/bin/env -S python3 -B
# coding: utf-8

"""
    This script sets up a fresh debian install to a known configuration

    Warning: unless you are me, don't run this script.

    You at a minimum need to change "user" to your user name, and "epwd" to your
    hashed-password
"""

from myutils import bash
import os
import pwd
from shlex import quote
import shutil
import sys


def update():
    apt = shutil.which('apt')
    bash(f'{apt} update')		
    bash(f'{apt} upgrade -y')		
    bash(f'{apt} install -y sudo htop git python3-pip psmisc neovim curl openssh-server')		

def hostname():
    # set up computers list
    computers = [("km1", "192.168.56.50"),
                 ("kw1", "192.168.56.60")]
    domain = "lan"

    # Write the hostname to /etc/hostname
    with open('/etc/hostname', 'w') as file:
        file.write(f"{computers[0][0]}\n")

    # Set up the /etc/hosts file
    with open('/etc/hosts', 'r') as f:
        lines = f.readlines()

    # check if localhost is set to 127.0.0.1
    if not any('127.0.0.1' in line and 'localhost' in line for line in lines):
        # Add the localhost mapping if it doesn't exist
        with open('/etc/hosts', 'a') as f:
            f.write('127.0.0.1\tlocalhost\n')

    # Set up the mappings for all machines in the computers list
    entries = []
    for computer in computers:
        entry = f'{computer[1]}\t{computer[0]} {computer[0]}.{domain}'
        entries.append(entry)

   # Add the entries into the /etc/hosts file 
    with open('/etc/hosts', 'a') as f:
        f.write('\n')
        f.write('\n'.join(entries))

def envVar():
    # set up environment variables
    shutil.copy('environment', '/etc/')
    os.chmod('/etc/environment',0o644)

def setupUser(user):
    # Check if the current user is a member of the sudo, or data group
    groups = bash(f'groups {user}').strip().split()
    is_sudo = 'sudo' in groups
    is_data = 'data' in groups

    # Add the user to any missing groups
    if not is_sudo or not is_data:
        groups_to_add = []
        if not is_sudo:
            groups_to_add.append('sudo')
        if not is_data:
            groups_to_add.append('data')
        usermod = shutil.which('usermod')
        bash(f'{usermod} -aG {" ".join(groups_to_add)} {user}')

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

    update-grub = shutil.which('update-grub')
    bash(f'{update-grub}')

def main(args):
    # Check that script is running with root privleges
    if os.geteuid() != 0:
        print("This script must be run as a privileged user or with the sudo command.")
        exit(1)

    user = quote('phil')

    try:
        pwd.getpwname(user)
    except KeyError:
        useradd = shutil.which('useradd')
        bash(f'{useradd} -m -s /bin/bash {user}')

    update()
    # networkInterface()
    hostname()
    envVar()
    setupUser(user)
    grub()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
