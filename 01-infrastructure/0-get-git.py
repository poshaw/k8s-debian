#! /usr/bin/env -S python3 -B
# coding: utf-8

from myutils import bash
import os
import shutil
import sys

user = 'phil'

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
    email = 'poadshaw@gmail.com'
    bash(f'{git} config --global user.email "{email}"')		

    # name default branch for new repos
    bash(f'{git} config --global init.defaultBranch "master"')

    # set merge strategy
    bash(f'{git} config --global pull.rebase false')

def setup_ssh_to_github():
    sshdir = f'/home/{user}/.ssh'
    if not os.path.exists(sshdir):
        os.mkdir(sshdir)
        os.chmod(sshdir,0o700)
    keydir = '/mnt/shared/ssh'
    if os.path.exists(keydir):
        shutil.copytree(keydir,sshdir, dirs_exist_ok=True)
        uid = int(bash(f'/usr/bin/id -u {user}'))
        gid = int(bash(f'/usr/bin/id -g {user}'))
        bash(f'/usr/bin/chown --recursive {uid}:{gid} {sshdir}')
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
