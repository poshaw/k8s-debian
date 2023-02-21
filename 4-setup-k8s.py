#! /usr/bin/env -S python3 -B
# coding: utf-8

"""
    This script sets up k8s on a mostly fresh install of Debian 11

    execution command:
    $ ./2-setup-k8s.py

    Pre-requisits on system: sudo curl openssh-server		

    This script should be run as a user with sudo privilages
    on the master server.  master should be able to ssh into
    worker server using passwordless ssh key-pair
    
    Ensure "worker" and "master" are named appropriately
"""

import getpass
from myutils import bash
from os import mkdir, path
from re import sub
from shlex import split
from subprocess import Popen, PIPE

user = getpass.getuser()
password = getpass.getpass(prompt = 'Enter sudo password: ')
worker = 'kw1.lan'
master = 'km1.lan'
CIDR='10.100.0.0/16'
kubedir = path.join(path.expanduser('~'), '.kube')
kubeconf = path.join(path.expanduser('~'), '.kube', 'config')
yamldir = path.join(path.expanduser('~'), 'yaml')
calico =  path.join(yamldir, 'calico.yaml')
sudo = '/usr/bin/sudo -S'

def cleanup():
    # reset worker
    bash(f'/usr/bin/ssh {user}@{worker} "{sudo} /usr/bin/kubeadm reset --force"', stdin=PIPE)

    # reset master
    bash(f'{sudo} /usr/bin/kubeadm reset --force', input=password)
    bash(f'/usr/bin/rm -rf {kubedir}')

cleanup()

# initialize master
bash(f'{sudo} /usr/bin/kubeadm config images pull', input=password)
bash(f'{sudo} /usr/bin/kubeadm init --control-plane-endpoint={master}:6443 --pod-network-cidr={CIDR}', input=password)
bash(f'/usr/bin/mkdir {kubedir}')
bash(f'{sudo} /usr/bin/kubeadm config images pull', input=password)
bash(f'{sudo} /usr/bin/cp -i /etc/kubernetes/admin.conf {kubeconf}', input=password)
uid = int(bash('/usr/bin/id -u'))
gid = int(bash('/usr/bin/id -g'))
bash(f'{sudo} /usr/bin/chown {uid}:{gid} {kubeconf}', input=password)

bash('/usr/bin/kubectl cluster-info')

bash('/usr/bin/kubectl cluster-info')

# have worker join the cluster
join_command = bash('/usr/bin/kubeadm token create --print-join-command', stdout=PIPE)
bash(f'/usr/bin/ssh {user}@{worker} "{sudo} {join_command}"', input=password)

# downlowd calico.yaml for network config
if not path.exists(yamldir):
    mkdir(yamldir)
bash(f'/usr/bin/curl --fail --silent --show-error --location --output {calico} \
    https://docs.projectcalico.org/manifests/calico.yaml')

bash(f'/usr/bin/cp {calico} {calico}_bak')

with open(calico, 'r') as file:
    text = file.readlines()

# regex for a vaild ipv4 address
validip = r"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
i=0
while i < len(text):
    if 'CALICO_IPV4POOL_CIDR' in text[i]:
        text[i] = text[i].replace('# ','')
        text[i+1] = text[i+1].replace('# ','')
        text[i+1] = sub(validip, CIDR[:-3], text[i+1])
        break
    i += 1

with open(calico, 'w') as file:
    file.writelines(text)

bash(f'/usr/bin/kubectl apply -f {calico}')
bash('/usr/bin/kubectl get nodes')
