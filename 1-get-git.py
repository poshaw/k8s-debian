#! /usr/bin/python3 -B

from getpass import getpass
from shlex import split
from shutil import copy as shutilcopy
from subprocess import Popen, PIPE

user = 'phil'
# password = getpass(prompt = 'Enter root password: ')
# password = bytes(password, 'utf-8')

def bash(command, *, input=None, stdin=None, stdout=None, stderr=None):
    if input is not None:
        stdin=PIPE
    command = split(command)
    p = Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)
    outs, errs = p.communicate(input)
    p.wait()
    if outs is not None:
        return outs.decode('utf-8')[:-1]

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

bash('/usr/bin/git config --global init.defaultBranch "master"')
