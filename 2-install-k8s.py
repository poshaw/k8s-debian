#! /usr/bin/env -S python3 -B
# coding: utf-8

from subprocess import run, PIPE
from myutils import bash
import os
import shlex
import shutil
import sys
from urllib.request import urlopen

def check_swap():
    cmd = "free | awk '/^Swap:/ {exit !($2+$3)}'"
    result = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    return result.returncode == 0 and int(result.stdout.strip()) > 0

def load_kernel_modules():
    modprobe = shutil.which('modprobe')
    bash(f"{modprobe} overlay")
    bash(f"{modprobe} br_netfilter")
    path = '/etc/modules-load.d'
    src = 'k8s-modules.conf'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)

def download_key(url):
    with urlopen(url) as response:
        return response.read()

def add_key(key):
    cmd = shlex.split(f"{shutil.which('gpg')} --dearmor -o /etc/apt/trusted.gpg.d/docker.gpg")
    try:
        result = run(cmd, input=key, stdout=PIPE, stderr=PIPE, check=True)
    except CalledProcessError as e:
        print(f"Error: {e.stderr.decode().strip()}")
        sys.exit(1)

    return result.stdout.decode().strip()

def main(argv):
    # Check that script is running with root privleges
    if os.geteuid() != 0:
        print("This script must be run as a privileged user or with the sudo command.")
        return 1

    # check for swap
    if check_swap():
        print("Swap is enabled on this system.  Disable swap and re-run this script.")
        return 1
    else:
        print("No Swap is enabled, you're good to proceed!")

    load_kernel_modules()

    url = "https://download.docker.com/linux/debian/gpg"
    key = download_key(url)
    add_key(key)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
