#! /usr/bin/env -S python3 -B
# coding: utf-8

import shlex
import subprocess

def runc(cmd, input=None):
    cmd_list = shlex.split(cmd)
    result = subprocess.run(
        cmd_list,
        input=input.encode('utf-8') if input else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout, result.stderr
