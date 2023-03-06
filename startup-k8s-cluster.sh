#! /usr/bin/env python3
# coding: utf-8

import getpass
import subprocess
import os
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
        subprocess.run(split(f'/usr/bin/ssh {user}@{node} "{sudo} /usr/bin/kubeadm reset --force"'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    subprocess.run(split(f'{sudo} /usr/bin/rm -rf {kubedir}'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def initialize_master():
    subprocess.run(split(f'{sudo} /usr/bin/kubeadm config images pull'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(split(f'{sudo} /usr/bin/kubeadm init --control-plane-endpoint={nodes[0]}:6443 --pod-network-cidr={CIDR}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(split(f'/usr/bin/mkdir {kubedir}'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(split(f'{sudo} /usr/bin/kubeadm config images pull'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    uid = os.getuid()
    gid = os.getgid()
    subprocess.run(split(f'{sudo} /usr/bin/cp -i /etc/kubernetes/admin.conf {kubeconf}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(split(f'{sudo} /usr/bin/chown {uid}:{gid} {kubeconf}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

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
