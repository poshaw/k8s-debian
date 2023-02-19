#! /usr/bin/env python3
# coding: utf-8

from shlex import split
from subprocess import Popen, PIPE

def bash(command, *, input=None, stdin=None, stdout=None, stderr=None):
    """
    Execute a shell command and return its output as a string.

    Args:
        command (str): The command to execute.
        input (bytes, optional): The input to feed to the command's stdin. Defaults to None.
        stdin (file-like object, optional): The stdin to use for the command. Defaults to None.
        stdout (file-like object, optional): The stdout to use for the command. Defaults to None.
        stderr (file-like object, optional): The stderr to use for the command. Defaults to None.

    Returns:
        str: The output of the command, with trailing newline characters removed.

    Raises:
        TypeError: If input is provided but is not a bytes object.

    Usage:
        >>> output = bash('ls -la')
        >>> print(output)

    This function is intended for use in a Unix-like environment with a Bash shell.
    For more information, see the project documentation at https://github.com/myproject/mymodule.
    """


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
