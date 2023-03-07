import logging
import shlex
import subprocess

def runc(cmd, input=None):
    cmd_list = shlex.split(cmd)
    if isinstance(input, str):
        input = input.encode('utf-8')
    elif isinstance(input, bytes):
        input = input.decode('utf-8').encode('utf-8')
    result = subprocess.run(
        cmd_list,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )
    return result.stdout, result.stderr

def handle_error(script_name, line_number, error):
    logging.error(f"{script_name}:{line_number} - An error occurred: {error}")
