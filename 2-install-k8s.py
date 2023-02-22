#! /usr/bin/env -S python3 -B
# coding: utf-8

import os
import shlex
import shutil
from subprocess import CalledProcessError, PIPE, run
import sys
from urllib.request import urlopen

def check_swap():
    cmd = "free | awk '/^Swap:/ {exit !($2+$3)}'"
    result = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    return result.returncode == 0 and int(result.stdout.strip()) > 0

def load_kernel_modules():
    cmd = shlex.split(f"{shutil.which('modprobe')} overlay")
    run(cmd, check=True)
    cmd = shlex.split(f"{shutil.which('modprobe')} br_netfilter")
    run(cmd, check=True)

    path = '/etc/modules-load.d'
    src = 'k8s-modules.conf'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)

    path = '/etc/sysctl.d'
    src = 'k8s.conf'
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

def apt_update():
    cmd = shlex.split(f"{shutil.which('apt')} update")
    run(cmd, check=True)

def install(packages):
    cmd = shlex.split(f"{shutil.which('apt')} install -y") + packages
    run(cmd, check=True)

def modify_containerd_config():
    # Open config.toml in inplace mode, allowing modifications to be made
    with fileinput.input('/etc/containerd/config.toml', inplace=True) as f:
        for line in f:
            # Look for the SystemdCgroup setting and modify it
            if 'SystemdCgroup' in line:
                line = 'SystemdCgroup = true\n'
            # Print the modified or unmodified line to stdout
            print(line, end='')
            
def main(argv):
    # Check that script is running with root privleges
    if os.geteuid() != 0:
        print("This script must be run as a privileged user or with the sudo command.")
        return 1

    # Install dependencies
    apt_update()
    packages = ["curl", "gnupg2", "software-properties-common", "apt-transport-https", "ca-certificates"]
    install(packages)

    # Add Docker repository key
    url = "https://download.docker.com/linux/debian/gpg"
    key = download_key(url)
    add_key(key)

    # Add Docker repository
    distro = run(['lsb_release', '-cs'], check=True, stdout=PIPE, text=True).stdout.strip()
    repo = f"deb [arch=amd64] https://download.docker.com/linux/debian {distro} stable"
    run(['add-apt-repository', repo], check=True)

    # install containerd
    apt_update()
    install(['containerd.io'])

    # check for swap
    if check_swap():
        print("Swap is enabled on this system.  Disable swap and re-run this script.")
        return 1
    else:
        print("No Swap is enabled, you're good to proceed!")

    load_kernel_modules()
    
    # configure containerd
    cmd = "containerd config default"
    result = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if result.returncode == 0:
        with open('/etc/containerd/config.toml', 'w') as f:
            f.write(result)

    modify_containerd_config()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
