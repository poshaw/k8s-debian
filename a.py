#! /usr/bin/env -S python3 -B
# coding: utf-8

import getpass
import logging
import os
import re
import shutil
import subprocess
import sys
from myutils import handle_error, runc

logging.basicConfig(level=logging.INFO)

user = getpass.getuser()
password = getpass.getpass(prompt='Enter sudo password: ')
print(f"Password type: {type(password)}")
nodes = ['km1.lan', 'kw1.lan']
CIDR = '10.100.0.0/16'
kubedir = os.path.join(os.path.expanduser('~'), '.kube')
kubeconf = os.path.join(os.path.expanduser('~'), '.kube', 'config')
yamldir = os.path.join(os.path.expanduser('~'), 'yaml')
calico = os.path.join(yamldir, 'calico.yaml')


def rename_worker(workers):
    for worker in workers:
        logging.info(f'Setting role to worker for {worker} to the cluster...')
        cmd = f'kubectl label nodes {worker} node-role.kubernetes.io/worker""'
        stdout, stderr = runc(cmd)
    
def main(args):
    try:
        rename_worker(nodes[1:])
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
