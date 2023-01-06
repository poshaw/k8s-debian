#! /usr/bin/python3 -B

from getpass import getpass
from myutils import bash
from shlex import split
from shutil import copy as shutilcopy
from subprocess import Popen, PIPE

user = 'phil'
# password = getpass(prompt = 'Enter root password: ')
# password = bytes(password, 'utf-8')

# update the system
bash('/usr/bin/apt update')		
bash('/usr/bin/apt upgrade -y')		

# install packages
bash('/usr/bin/apt install -y git')		

# set username
bash('/usr/bin/git config --global user.name "poshaw"')		
bash('/usr/bin/git config --global user.name')		

# set email
bash('/usr/bin/git config --global user.email "poadshaw@gmail.com"')		
bash('/usr/bin/git config --global user.email')		

# name default branch for new repos
bash('/usr/bin/git config --global init.defaultBranch "master"')
