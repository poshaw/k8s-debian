#! /usr/bin/env -S python3 -B
# coding: utf-8

from subprocess import run, PIPE
from shlex import split

def bash(command, *, input=None):
    if input is not None:
        if not isinstance(input, bytes):
            input = input.encode('utf-8')
        result = run(split(command), input=input, stdout=PIPE, stderr=PIPE, text=True, check=True)
    else:
        result = run(split(command), stdout=PIPE, stderr=PIPE, text=True, check=True)
    return result.stdout.rstrip()
