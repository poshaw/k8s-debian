#! /usr/bin/env -S python3 -B
# coding: utf-8

from myutils import bash
import shutil
import subprocess
import sys

def check_swap():
    cmd = "free | awk '/^Swap:/ {exit !($2+$3)}'"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0 and int(result.stdout.strip()) > 0

def load_kernel_modules():
    modprobe = shutil.which('modprobe')
    bash(f"{modprobe} overlay")
    bash(f"{modprobe} br_netfilter")

    # load modules at each boot
    path = '/etc/modules-load.d'
    src = 'k8s-modules.conf'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)

    # set k8s kernel parameters
    path = '/etc/sysctl.d'
    src = 'k8s.conf'
    dst = os.path.join(path,src)
    shutil.copyfile(src, dst)

    sysctl = shutil.which('sysctl')
    bash(f"{sysctl} --system")
    

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

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
