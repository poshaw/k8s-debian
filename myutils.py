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
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    function_name = f.f_code.co_name
    logging.error(f"{script_name}:{filename}:{function_name}:{lineno} - An error occurred: {error}")
