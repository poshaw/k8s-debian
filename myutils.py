#! /usr/bin/env -S python3 -B
# coding: utf-8

from subprocess import run, PIPE
from shlex import split

def bash(command, *, input=None):
    if input is not None:
        stdin = PIPE
        if not isinstance(input, bytes):
            raise TypeError('input must be type: bytes')
        input = input.decode('utf-8')
    else:
        stdin = None
    
    # Run the command and capture the output
    result = run(split(command), input=input, stdin=stdin, stdout=PIPE, stderr=PIPE, text=True, check=True)
    return result.stdout.rstrip()
