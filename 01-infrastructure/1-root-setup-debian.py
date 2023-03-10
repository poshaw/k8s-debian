#! /usr/bin/env -S python3 -B
# coding: utf-8

"""
    This script sets up a fresh debian install to a known configuration

    Warning: unless you are me, don't run this script.

    You at a minimum need to change "user" to your user name, and "epwd" to your
    hashed-password
"""

from myutils import bash
from grp import getgrnam
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
    hostname = input("Enter computer hostname: ")
    domain = 'lan'

    with open('/etc/hostname', 'w') as f:
        f.write(hostname)

    path = '/etc'
    src = 'hosts'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)
    with open('/etc/hosts', 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if '127.0.1.1' in line:
            lines[i] = f'127.0.1.1\t{hostname} {hostname}.{domain}\n'
            break

    with open('/etc/hosts', 'w') as f:
        f.writelines(lines)
            
def envVar():
    # set up environment variables
    shutil.copy('environment', '/etc/')
    os.chmod('/etc/environment',0o644)

def setupUser(user):
    # Check if group data exists
    groupname = "data"
    try:
        getgrnam(groupname)
    except KeyError:
        bash(f"groupadd {groupname}")
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

    update_grub = shutil.which('update-grub')
    bash(f'{update_grub}')

def networkInterface():
    # TODO change this to eth0 and then modify based on hostname?
    path = '/etc/network'
    src = 'interfaces'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)
    path = '/etc/network/interfaces.d'
    src = 'enp0s3'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)
    src = 'enp0s8'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)

    # restart the computer
    halt = shutil.which('halt')
    bash(f'{halt} --reboot --force')	

def main(args):
    # Check that script is running with root privleges
    if os.geteuid() != 0:
        print("This script must be run as a privileged user or with the sudo command.")
        exit(1)

    user = quote('phil')
    try:
        pwd.getpwnam(user)
    except KeyError:
        useradd = shutil.which('useradd')
        bash(f'{useradd} -m -s /bin/bash {user}')

    update()
    hostname()
    envVar()
    setupUser(user)
    grub()
    networkInterface()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
