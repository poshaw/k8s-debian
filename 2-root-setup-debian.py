#! /usr/bin/python3 -B

from getpass import getpass
from shlex import split
from shutil import copy as shutilcopy
from subprocess import Popen, PIPE

user = 'phil'
# password = getpass(prompt = 'Enter root password: ')
# password = bytes(password, 'utf-8')

def bash(command, *, input=None, stdin=None, stdout=None, stderr=None):
    if input is not None:
        stdin=PIPE
    command = split(command)
    p = Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)
    outs, errs = p.communicate(input)
    p.wait()
    if outs is not None:
        return outs.decode('utf-8')[:-1]

# update the system
bash('/usr/bin/apt update')		
bash('/usr/bin/apt upgrade -y')		

# install packages
bash('/usr/bin/apt install -y sudo htop git python3-pip psmisc neovim curl openssh-server')		

# set up environment variables
shutilcopy('/mnt/shared/environment', '/etc/')
bash('/usr/bin/chmod 0644 /etc/environment')		

# modify user
bash('/usr/sbin/usermod -a -G sudo,vboxsf phil')		
epwd = '$y$j9T$kClTc051lMiQ3YJHoyNhY0$Xv0m9Bc6kntTwerKAIH0LujrvWFkrxtsxFJm1o5v4e0'
epwd = bytes(f'{user}:{epwd}', 'utf-8')
bash('/usr/sbin/chpasswd --encrypted', input=epwd)

# fix grub timeout
with open('/etc/default/grub', 'r') as file:
    text = file.readlines()

for i, line in enumerate(text):
    if 'GRUB_TIMEOUT' in line:
        text[i] = line.replace('5', '0')
        break

with open('/etc/default/grub', 'w') as file:
    file.writelines(text)

bash('/usr/sbin/update-grub')		
