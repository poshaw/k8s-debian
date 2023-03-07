import inspect
import logging
import shlex
import subprocess

def runc(cmd, input=None):
    cmd_list = shlex.split(cmd)
    result = subprocess.run(
        cmd_list,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )
    return result.stdout, result.stderr

def handle_error(script_name, error):
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno
    logging.error(f"{script_name}:{function_name}:{line_number} - An error occurred: {error}")
