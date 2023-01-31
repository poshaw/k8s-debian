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
    # update the system
    bash('/usr/bin/apt update')		
    bash('/usr/bin/apt upgrade -y')		

    # install packages
    bash('/usr/bin/apt install -y sudo htop git python3-pip psmisc neovim curl openssh-server')		

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
    envvar()
    user()
    grub()
    return 0

if __name__ == "__main__":
    exit(main(argv[1:]))
