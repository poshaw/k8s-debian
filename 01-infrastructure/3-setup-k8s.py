#! /usr/bin/env -S python3 -B
# coding: utf-8

import getpass
from myutils import bash
from os import mkdir, path
from re import sub
from shlex import split

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
    bash(f'/usr/bin/ssh {user}@{worker} "{sudo} /usr/bin/kubeadm reset --force"', input=password)

    # reset master
    bash(f'{sudo} /usr/bin/kubeadm reset --force', input=password)
    bash(f'/usr/bin/rm -rf {kubedir}')

def initialize_master():
    bash(f'{sudo} /usr/bin/kubeadm config images pull', input=password)
    bash(f'{sudo} /usr/bin/kubeadm init --control-plane-endpoint={master}:6443 --pod-network-cidr={CIDR}', input=password)
    bash(f'/usr/bin/mkdir {kubedir}')
    bash(f'{sudo} /usr/bin/kubeadm config images pull', input=password)
    bash(f'{sudo} /usr/bin/cp -i /etc/kubernetes/admin.conf {kubeconf}', input=password)
    uid = int(bash('/usr/bin/id -u'))
    gid = int(bash('/usr/bin/id -g'))
    bash(f'{sudo} /usr/bin/chown {uid}:{gid} {kubeconf}', input=password)

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
    cleanup()
    initialize_master()

    bash('/usr/bin/kubectl cluster-info')

    worker_join_cluster()

    setup_calico()
    bash('/usr/bin/kubectl get nodes')

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
