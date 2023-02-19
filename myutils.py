#! /usr/bin/env python3
# coding: utf-8

from shlex import split
from subprocess import Popen, PIPE

def bash(command, *, input=None, stdin=None, stdout=None, stderr=None):
    if input is not None:
        stdin=PIPE
        if not isinstance(input, bytes):
            raise TypeError('input must be type: bytes')
    command = split(command)
    p = Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)
    outs, errs = p.communicate(input)
    p.wait()
    if outs is not None:
        outs = outs.decode('utf-8').rstrip()
        return outs
