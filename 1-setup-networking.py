#! /usr/bin/env -S python3 -B
# coding: utf-8

from myutils import bash
import os
import shutil
import socket
import sys

def hostname():
    hostname = input("Enter computer hostname: ")
    domain = 'lan'

    echo = shutil.which('echo')
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

    hostname()
    # networkInterface()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
