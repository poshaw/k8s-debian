poadshaw@gmail.com#! /usr/bin/python3
# -*- coding: utf-8 -*-

from myutils import bash
from shlex import split
from sys import exit, argv

user = 'poshaw'
email = 'poadshaw@gmail.com'

def install_git():
	# update the system
	bash('/usr/bin/apt update')		
	bash('/usr/bin/apt upgrade -y')		

	# install packages
	bash('/usr/bin/apt install -y git')		

def configure_git():
	# set username
	bash(f'/usr/bin/git config --global user.name "{user}"')		

	# set email
	bash('/usr/bin/git config --global user.email "{email}"')		

	# name default branch for new repos
	bash('/usr/bin/git config --global init.defaultBranch "master"')

def main(args):
	install_git()
	configure_git()
	return 0

if __name__ == "__main__":
	exit(main(argv[1:]))
