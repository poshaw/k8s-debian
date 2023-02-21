#! /usr/bin/env -S python3 -B
# coding: utf-8

from myutils import bash
import os
import shutil
import sys

def networkInterface():
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

    networkInterface()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
