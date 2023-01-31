#! /usr/bin/env python
# coding utf-8

import getpass
from os import mkdir, path
from re import sub
from shlex import split
from subprocess import Popen, PIPE

user = getpass.getuser()
password = getpass.getpass(prompt = 'Enter sudo password: ')
password = bytes(password, 'utf-8')
worker = 'kw1.lan'
master = 'km1.lan'
CIDR='10.100.0.0/16'
kubedir = path.join(path.expanduser('~'), '.kube')
kubeconf = path.join(path.expanduser('~'), '.kube', 'config')
yamldir = path.join(path.expanduser('~'), 'yaml')
calico =  path.join(yamldir, 'calico.yaml')
sudo = '/usr/bin/sudo -S'

def bash(command, *, stdin=None, stdout=None, stderr=None):
    command = split(command)
    p = Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)
    if stdin is not None:
        outs, errs = p.communicate(input=password)
    else:
        outs, errs = p.communicate()
    p.wait()
    if outs is not None:
        return outs.decode('utf-8')[:-1]

def cleanup():
    # reset worker
    bash(f'/usr/bin/ssh {user}@{worker} "{sudo} /usr/bin/kubeadm reset --force"', stdin=PIPE)

    # reset master
    bash(f'{sudo} /usr/bin/kubeadm reset --force', stdin=PIPE)
    bash(f'/usr/bin/rm -rf {kubedir}')

cleanup()

# initialize master
bash(f'{sudo} /usr/bin/kubeadm config images pull', stdin=PIPE)
bash(f'{sudo} /usr/bin/kubeadm init --control-plane-endpoint={master}:6443 --pod-network-cidr={CIDR}', stdin=PIPE)
bash(f'/usr/bin/mkdir {kubedir}')
bash(f'{sudo} /usr/bin/kubeadm config images pull', stdin=PIPE)
bash(f'{sudo} /usr/bin/cp -i /etc/kubernetes/admin.conf {kubeconf}', stdin=PIPE)
uid = int(bash('/usr/bin/id -u', stdout=PIPE))
gid = int(bash('/usr/bin/id -g', stdout=PIPE))
bash(f'{sudo} /usr/bin/chown {uid}:{gid} {kubeconf}', stdin=PIPE)

bash('/usr/bin/kubectl cluster-info')

bash('/usr/bin/kubectl cluster-info')

# have worker join the cluster
join_command = bash('/usr/bin/kubeadm token create --print-join-command', stdout=PIPE)
bash(f'/usr/bin/ssh {user}@{worker} "{sudo} {join_command}"', stdin=PIPE)

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
    i += 1

with open(calico, 'w') as file:
    file.writelines(text)

bash(f'/usr/bin/kubectl apply -f {calico}')
bash('/usr/bin/kubectl get nodes')
