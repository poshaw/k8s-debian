#! /usr/bin/env -S python3 -B
# coding: utf-8

import getpass
import logging
from myutils import handle_error, runc
import os
import re
import shutil
import subprocess
import sys
import time

logging.basicConfig(level=logging.INFO)

user = getpass.getuser()
password = getpass.getpass(prompt='Enter sudo password: ')
nodes = ['km1.lan', 'kw1.lan']
CIDR = '10.100.0.0/16'
kubedir = os.path.join(os.path.expanduser('~'), '.kube')
kubeconf = os.path.join(os.path.expanduser('~'), '.kube', 'config')

def reset_cluster(workers):
    logging.info('Resetting K8S cluster...')
    for worker in workers:
        logging.info(f'Resetting worker {worker}...')
        cmd = f'ssh {user}@{worker} "sudo -S systemctl stop kubelet"'
        stdout, stderr = runc(cmd, input=password)
        cmd = f'ssh {user}@{worker} "sudo -S systemctl disable kubelet"'
        stdout, stderr = runc(cmd, input=password)
        cmd = f'ssh {user}@{worker} "sudo -S kubeadm reset --force"'
        stdout, stderr = runc(cmd, input=password)
        cmd = f'ssh {user}@{worker} "sudo -S systemctl enable kubelet"'
        stdout, stderr = runc(cmd, input=password)
        cmd = f'ssh {user}@{worker} "sudo -S systemctl start kubelet"'
        stdout, stderr = runc(cmd, input=password)
            
    logging.info('Resetting K8S master...')
    cmd = 'sudo -S kubeadm reset --force'
    stdout, stderr = runc(cmd, input=password)
    cmd = f'sudo rm -rf /etc/cni/net.d/*'
    stdout, stderr = runc(cmd, input=password)
    cmd = f'rm -rf {kubedir}'
    stdout, stderr = runc(cmd)
    if stderr:
        logging.error(f'Error cleaning up {kubedir}: {stderr}')
    
    logging.info('K8S cluster reset successfully.')

def initialize_master(master):
    logging.info('Pulling images...')
    cmd = 'sudo -S kubeadm config images pull'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        logging.error(f'Error pulling images: {stderr}')
        return

    logging.info('Initializing master...')
    cmd = f'sudo -S kubeadm init --control-plane-endpoint={master}:6443 --pod-network-cidr={CIDR}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        logging.error(f'Error initializing master: {stderr}')
        return

    os.makedirs(kubedir, exist_ok=True)

    logging.info('Copying config file...')
    cmd = f'sudo -S cp -i /etc/kubernetes/admin.conf {kubeconf}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        logging.error(f'Error copying directory {kubedir}: {stderr}')
        return

    uid = os.getuid()
    gid = os.getgid()
    
    cmd = f'sudo -S chown {uid}:{gid} {kubeconf}'
    stdout, stderr = runc(cmd, input=password)
    if stderr:
        logging.error(f'Error changing permission of {kubeconf} to {uid}:{gid}: {stderr}')
        return
    
    logging.info('Initialization of master node completed successfully.')

def worker_join_cluster(workers, join_command):
    for worker in workers:
        logging.info(f'Joining worker {worker} to the cluster...')
        cmd = f'ssh {user}@{worker} "sudo -S {join_command}"'
        stdout, stderr = runc(cmd, input=password)
        if stderr:
            logging.error(f'Error joining worker {worker} to the cluster: {stderr}')
        else:
            logging.info(f'Worker {worker} joined the cluster successfully.')
        logging.info(f'Setting role to worker for {worker} to the cluster...')
        node_name = worker.split(".")[0]
        cmd = f'kubectl label nodes {node_name} node-role.kubernetes.io/worker=worker --overwrite'
        stdout, stderr = runc(cmd)
        if stderr:
            logging.error(f'Error setting role to worker for {worker}: {stderr}')
        else:
            logging.info(f'Worker {worker} labeled successfully.')
    
def setup_calico():
    cmd_apply = f'kubectl apply -f config/01-calico.yaml'
    stdout, stderr = runc(cmd_apply)
    if stderr:
        logging.error(f'Error applying calico configuration: {stderr}')
        return

    logging.info('Calico configuration applied successfully.')
        
def setup_storage(server):
    cmd = f'ssh {user}@{server} "sudo -S mkdir -p /mnt/cluster-storage"'
    stdout, stderr = runc(cmd, input=password)

def k8s_status():
    cmd = 'kubectl cluster-info'
    stdout, stderr = runc(cmd)
    logging.info(stdout)
    # loop until all nodes are ready or timeout (5 min) occurs
    timeout = 300
    start_time = time.time()
    cmd = 'kubectl get nodes'
    while True:
        stdout, stderr = runc(cmd)
        lines = stdout.strip().split("\n")
        not_ready_nodes = [line for line in lines[1:] if "NotReady" in line]
        if not_ready_nodes:
            logging.info(f"{len(not_ready_nodes)} node(s) not ready yet: {', '.join(not_ready_nodes)}")
            time.sleep(5)
        else:
            logging.info("All nodes are ready!")
            break
    
def main(args):
    try:
        reset_cluster(nodes[1:])
        initialize_master(nodes[0])
        join_command = runc('kubeadm token create --print-join-command')[0].strip()
        worker_join_cluster(nodes[1:], join_command)
        setup_calico()
        setup_storage('kw1.lan')
        k8s_status()
    except FileNotFoundError as e:
        handle_error(__file__, e)
    except PermissionError as e:
        handle_error(__file__, e)
    except Exception as e:
        handle_error(__file__, e)
    else:
        logging.info("Script completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    sys.exit(main(sys.argv[1:]))
