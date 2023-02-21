#! /usr/bin/env -S python3 -B
# coding: utf-8

from myutils import bash
import os
import shutil
from subprocess import PIPE
import sys

user = 'phil'
email = 'poadshaw@gmail.com'
keydir = '/mnt/shared/ssh'

def install_git():
    # update the system
    apt = shutil.which('apt')
    bash(f'{apt} update')		
    bash(f'{apt} upgrade -y')		
    bash(f'{apt} install -y git openssh-server')	

def configure_git():
    # set username
    git = shutil.which('git')
    bash(f'{git} config --global user.name "{user}"')		

    # set email
    bash(f'{git} config --global user.email "{email}"')		

    # name default branch for new repos
    bash(f'{git} config --global init.defaultBranch "master"')

    # set merge strategy
    bash(f'{git} config --global pull.rebase false')

def setup_ssh_to_github():
    sshdir = f'/home/{user}/.ssh'
    if not os.path.exists(sshdir):
        os.mkdir(sshdir)
    # bash(f'/usr/bin/cp {keydir}/* {sshdir}')
    shutil.copytree(keydir,sshdir, dirs_exist_ok=True)
    uid = int(bash(f'/usr/bin/id -u {user}', stdout=PIPE))
    gid = int(bash(f'/usr/bin/id -g {user}', stdout=PIPE))
    bash(f'/usr/bin/chown --recursive {uid}:{gid} {sshdir}')
    os.chmod(sshdir,0o700)
    for file in os.listdir(sshdir):
        os.chmod(os.path.join(sshdir,file),0o644)
    os.chmod(os.path.join(sshdir, 'id_ed25519'),0o600)

def main(args):
    install_git()
    configure_git()
    # setup_ssh_to_github()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
