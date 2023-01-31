#! /usr/bin/env python
# coding: utf-8

from myutils import bash
from os import chmod, listdir, mkdir, path
from shlex import split
from shutil import copytree
from sys import exit, argv
from subprocess import PIPE
from sys import exit, argv

user = 'phil'
email = 'poadshaw@gmail.com'
keydir = '/mnt/shared/ssh'

def install_git():
    # update the system
    bash('/usr/bin/apt update')		
    bash('/usr/bin/apt upgrade -y')		

    # install packages
    bash('/usr/bin/apt install -y git openssh-server')	

def configure_git():
    # set username
    bash(f'/usr/bin/git config --global user.name "{user}"')		

    # set email
    bash(f'/usr/bin/git config --global user.email "{email}"')		

    # name default branch for new repos
    bash('/usr/bin/git config --global init.defaultBranch "master"')

def setup_ssh_to_github():
    sshdir = f'/home/{user}/.ssh'
    if not path.exists(sshdir):
        mkdir(sshdir)
    # bash(f'/usr/bin/cp {keydir}/* {sshdir}')
    copytree(keydir,sshdir, dirs_exist_ok=True)
    uid = int(bash(f'/usr/bin/id -u {user}', stdout=PIPE))
    gid = int(bash(f'/usr/bin/id -g {user}', stdout=PIPE))
    bash(f'/usr/bin/chown --recursive {uid}:{gid} {sshdir}')
    chmod(sshdir,0o700)
    for file in listdir(sshdir):
        chmod(path.join(sshdir,file),0o644)
    chmod(path.join(sshdir, 'id_ed25519'),0o600)


def main(args):
    install_git()
    configure_git()
    setup_ssh_to_github()
    return 0

if __name__ == "__main__":
    exit(main(argv[1:]))
