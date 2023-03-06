#! /usr/bin/env python3
2  # coding: utf-8
3
4  import getpass
5  import subprocess
6  import os
7  import sys
8
9  user = getpass.getuser()
10 password = getpass.getpass(prompt='Enter sudo password: ')
11 nodes = ['km1.lan', 'kw1.lan']
12 CIDR = '10.100.0.0/16'
13 kubedir = os.path.join(os.path.expanduser('~'), '.kube')
14 kubeconf = os.path.join(os.path.expanduser('~'), '.kube', 'config')
15 yamldir = os.path.join(os.path.expanduser('~'), 'yaml')
16 calico = os.path.join(yamldir, 'calico.yaml')
17 sudo = '/usr/bin/sudo -S'
18
19 def reset_cluster():
20     for node in nodes[1:]:
21         # reset node
22         subprocess.run(split(f'/usr/bin/ssh {user}@{node} "{sudo} /usr/bin/kubeadm reset --force"'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
23
24     subprocess.run(split(f'{sudo} /usr/bin/rm -rf {kubedir}'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
25
26 def initialize_master():
27     subprocess.run(split(f'{sudo} /usr/bin/kubeadm config images pull'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
28     subprocess.run(split(f'{sudo} /usr/bin/kubeadm init --control-plane-endpoint={nodes[0]}:6443 --pod-network-cidr={CIDR}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
29     subprocess.run(split(f'/usr/bin/mkdir {kubedir}'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
30     subprocess.run(split(f'{sudo} /usr/bin/kubeadm config images pull'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
31     uid = os.getuid()
32     gid = os.getgid()
33     subprocess.run(split(f'{sudo} /usr/bin/cp -i /etc/kubernetes/admin.conf {kubeconf}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
34     subprocess.run(split(f'{sudo} /usr/bin/chown {uid}:{gid} {kubeconf}'), input=password.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
35
36 def main(args):
37     cleanup()
38     initialize_master()
39
40     subprocess.run(split('/usr/bin/kubectl cluster-info'))
41
42 if __name__ == "__main__":
43     sys.exit(main(sys.argv[1:]))








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
