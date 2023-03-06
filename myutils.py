import shlex
import subprocess

def runc(cmd, input=None):
    cmd_list = shlex.split(cmd)
    stdin = subprocess.PIPE if input else None
    if isinstance(input, str):
        input = input.encode('utf-8')
    result = subprocess.run(
        cmd_list,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True,
        stdin=stdin
    )
    return result.stdout, result.stderr
