#! /usr/bin/env python3
# coding: utf-8

import getpass
from myutils import runc
import os
import shlex
import shutil
import subprocess
import sys

user = getpass.getuser()
password = getpass.getpass(prompt='Enter sudo password: ')
nodes = ['km1.lan', 'kw1.lan']
CIDR = '10.100.0.0/16'
kubedir = os.path.join(os.path.expanduser('~'), '.kube')
kubeconf = os.path.join(os.path.expanduser('~'), '.kube', 'config')
yamldir = os.path.join(os.path.expanduser('~'), 'yaml')
calico = os.path.join(yamldir, 'calico.yaml')
sudo = '/usr/bin/sudo -S'

def reset_cluster():
    for node in nodes[1:]:
        # reset node
        cmd = f'/usr/bin/ssh {user}@{node} "{sudo} /usr/bin/kubeadm reset --force"'
        stdout, stderr = runc(cmd, input=password)
        if stderr:
            print(f'Error resetting {node}: {stderr}')

    cmd = f'{sudo} /usr/bin/rm -rf {kubedir}'
    stdout, stderr = runc(cmd)
    if stderr:
        print(f'Error cleaning up {kubedir}: {stderr}')

def initialize_master():
    cmd = f'{sudo} {shutil.which("kubeadm")} config images pull'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        print(f'Error pulling images: {stderr}')

    cmd = f'{sudo} {shutil.which("kubeadm")} init --control-plane-endpoint={nodes[0]}:6443 --pod-network-cidr={CIDR}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        print(f'Error initializing master: {stderr}')

    cmd = f'{shutil.which("mkdir")} {kubedir}'
    stdout, stderr = runc(cmd)
    if stderr:
        print(f'Error creating directory {kubedir}: {stderr}')

    cmd = f'{sudo} {shutil.which("cp")} -i /etc/kubernetes/admin.conf {kubeconf}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        print(f'Error copying directory {kubedir}: {stderr}')

    uid = os.getuid()
    gid = os.getgid()
    
    cmd = f'{sudo} {shutil.which("chown")} {uid}:{gid} {kubeconf}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        print(f'Error changing permission of {kubeconf} to {uid}:{gid}: {stderr}')
    
def main(args):
    reset_cluster()
    initialize_master()

    subprocess.run(split('/usr/bin/kubectl cluster-info'))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

    
    
    



def worker_join_cluster():
    # have worker join the cluster
    join_command = bash('/usr/bin/kubeadm token create --print-join-command')
    bash(f'/usr/bin/ssh {user}@{worker} "{sudo} {join_command}"', input=password)

def setup_calico():
    # downlowd calico.yaml for network config
    if not path.exists(yamldir):
        mkdir(yamldir)
    bash(f'/usr/bin/curl --fail --silent --show-error --location --output {calico} \
        https://docs.projectcalico.org/manifests/calico.yaml')

    bash(f'/usr/bin/cp {calico} {calico}_bak')

    with open(calico, 'r') as f:
        lines = f.readlines()

    # regex for a vaild ipv4 address
    validip = r"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
    i=0
    while i < len(lines):
        if 'CALICO_IPV4POOL_CIDR' in lines[i]:
            lines[i] = lines[i].replace('# ','')
            lines[i+1] = lines[i+1].replace('# ','')
            lines[i+1] = sub(validip, CIDR[:-3], lines[i+1])
            break
        i += 1

    with open(calico, 'w') as file:
        file.writelines(lines)

    bash(f'/usr/bin/kubectl apply -f {calico}')

def main(args):
    reset_cluster()
    initialize_master()

    bash('/usr/bin/kubectl cluster-info')

    worker_join_cluster()

    setup_calico()
    bash('/usr/bin/kubectl get nodes')
