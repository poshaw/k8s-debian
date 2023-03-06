import shlex
import subprocess

def runc(cmd, input=None):
    cmd_list = shlex.split(cmd)
    if isinstance(input, str):
        input = input.encode('utf-8')
    result = subprocess.run(
        cmd_list,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )
    return result.stdout, result.stderr
