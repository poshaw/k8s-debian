#! /usr/bin/env -S python3 -B
# coding: utf-8

import logging
import sys
from myutils import handle_error, runc

logging.basicConfig(level=logging.INFO)

nodes = ['km1.lan', 'kw1.lan']

def rename_worker(workers):
    for worker in workers:
        node_name = worker.split(".")[0]
        logging.info(f'Setting role to worker for {worker} to the cluster...')
        cmd = f'kubectl label nodes {node_name} node-role.kubernetes.io/worker=worker --overwrite'
        stdout, stderr = runc(cmd)
        if stderr:
            logging.error(f'Error setting role to worker for {worker}: {stderr}')
        elif stdout:
            logging.info(f'Successfully set role to worker for {worker.split(".")[0]}: {stdout.strip()}')
        else:
            logging.info(f'Worker {worker} labeled successfully.')

def main(args):
    try:
        rename_worker(nodes[1:])
    except Exception as e:
        handle_error(__file__, e)
    else:
        logging.info("Script completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        logging.info('Script interrupted by user')
    except Exception as e:
        logging.exception('Unhandled exception occurred')
        raise e

