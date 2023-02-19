#! /usr/bin/env python
# coding: utf-8

"""
    This script sets up a fresh debian install to a known configuration

    Warning: unless you are me, don't run this script.

    You at a minimum need to change "user" to your user name, and "epwd" to your
    hashed-password
"""

from myutils import bash
import os
import pwd
from shlex import quote
import shutil
import sys


def update():
    """
    Updates the package list and upgrades all installed packages to their latest versions.

    This function uses the 'apt' package manager to update the system. It first updates the package
    list by downloading the latest package information from the software repositories. Then, it
    upgrades all currently installed packages to their latest versions. The '-y' flag is used to
    automatically answer 'yes' to all prompts.

    This function installs some commonly used packages such as 'sudo', 'htop', 'git', 'python3-pip',
    'psmisc', 'neovim', 'curl', and 'openssh-server'. You can customize the list of packages to
    install by modifying the 'bash' command inside this function.

    Note that this function requires superuser privileges to run, so it should be executed as a
    privileged user or with the 'sudo' command.

    Raises:
        subprocess.CalledProcessError: If the 'apt' command fails or returns a non-zero exit status.
    """

    apt = shutil.which('apt')
    bash(f'{apt} update')		
    bash(f'{apt} upgrade -y')		
    bash(f'{apt} install -y sudo htop git python3-pip psmisc neovim curl openssh-server')		

def networkinterface():
    try:
        import psutil
    except ModuleNotFoundError:
        print("psutil is not installed. Installing now...")
        bash(f'{sys.executable} -m pip install psutil')
        print("psutil installed. Restarting script...")
        os.execv(__file__, sys.argv)
    
    def list_interfaces_without_ip():
        interfaces = psutil.net_if_addrs()
        result = []
        for interface in interfaces:
            if not any(addr.family == 2 for addr in interfaces[interface]):
                result.append(interface)
        return result
    
    interfaces_without_ip = list_interfaces_without_ip()
    print(interfaces_without_ip)

def hostname():
    """
    Configures the hostname and IP address for the local machine by modifying the
    '/etc/hostname' and '/etc/hosts' files.

    This function sets the hostname of the machine by writing the first hostname-IP
    pair from the 'computers' list to the '/etc/hostname' file. It then sets up the
    IP address mappings for all machines in the 'computers' list in the '/etc/hosts'
    file. 

    Parameters:
        None

    Returns:
        None
    """
    
    # set up computers list
    computers = [("km1", "192.168.56.50"),
                 ("kw1", "192.168.56.60")]
    domain = "lan"

    # Write the hostname to /etc/hostname
    with open('/etc/hostname', 'w') as file:
        file.write(f"{computers[0][0]}\n")

    # Set up the /etc/hosts file
    with open('/etc/hosts', 'r') as f:
        lines = f.readlines()

    # check if localhost is set to 127.0.0.1
    found = False
    for line in lines:
        if '127.0.0.1' in line and 'localhost' in line:
            found = True
            break

    # Add the localhost mapping if it doesn't exist
    if not found:
        with open('/etc/hosts', 'a') as f:
            f.write('127.0.0.1\tlocalhost\n')

    # Set up the mappings for all machines in the computers list
    entries = []
    for computer in computers:
        entry = f'{computer[1]}\t{computer[0]} {computer[0]}.{domain}'
        entries.append(entry)

   # Add the entries into the /etc/hosts file 
    with open('/etc/hosts', 'a') as f:
        f.write('\n')
        f.write('\n'.join(entries))



def envvar():
    """
    Sets up the environment variables for the system by copying the `environment` file to `/etc/` and setting its permissions
    to read-only. The `environment` file contains environment variables for the system, such as `PATH`, `LANG`, and `LC_ALL`. 
    These environment variables affect how programs run on the system and can be customized to suit specific needs. By default, 
    this function sets up the environment variables for the current user, but you can modify the `environment` file to set up 
    environment variables for all users on the system.

    Raises:
        FileNotFoundError: If the `environment` file does not exist in the current working directory.
        PermissionError: If the script does not have permission to copy the `environment` file to `/etc/` or to change its permissions.
    """
    # set up environment variables
    shutil.copy('environment', '/etc/')
    os.chmod('/etc/environment',0o644)

def setupuser(user):
    """
    Modifies the user account by adding it to the 'sudo' and 'data' groups, and sets the user password.
    
    The 'sudo' group is necessary to grant the user superuser privileges, while the 'data' group is an example
    custom group that could be used for data-related operations. You can customize the list of groups by modifying
    the 'groups' variable inside this function.
    The user password is set by passing the hashed password to the 'chpasswd' command. The 'epwd' variable contains
    a sample hashed password for the user 'phil', which you should modify with your own hashed password before running
    the script. You can generate the hashed password using the 'mkpasswd' command on a Linux system.
    Note that this function requires superuser privileges to run, so it should be executed as a privileged user or
    with the 'sudo' command.
    """

    # Check if the current user is a member of the sudo, or data group
    is_sudo = False
    is_data = False
    groups = bash(f'groups {user}').strip().split()
    for group in groups:
        if group == 'sudo':
            is_sudo = True
        if group == 'data':
            is_data = True

    # If the user is not a member of the sudo group, add them to the group
    usermod = shutil.which('usermod')
    if not is_sudo:
        bash(f'{usermod} -aG sudo {user}')
    
    # If the user is not a member of the data group, add them to the group
    if not is_data:
        bash(f'{usermod} -aG data {user}')
    	
    # get hash via $ mkpasswd -m sha512crypt mypassword
    epwd = '$6$djg0mn/uDqZkGIFH$nizpdm1cChbWrMd2aNU3cRE6XeQOUu1gigMCPL/BnjJl1gbO9rgxn3EtKkPRx3Im6V/.oMG5TWGGcqgghRiwy0'
    epwd = bytes(f'{user}:{epwd}', 'utf-8')
    chpasswd = shutil.which('chpasswd')
    bash(f'{chpasswd} --encrypted', input=epwd)

def grub():
    """
    Configures the GRUB bootloader.
    
    This function modifies the configuration file for the GRUB bootloader to reduce the boot timeout
    from 5 seconds to 0 seconds, which will speed up the boot process. The 'update-grub' command is
    then used to update the GRUB configuration file based on the changes made.
    Note that this function requires superuser privileges to run, so it should be executed as a
    privileged user or with the 'sudo' command.
    Raises:
        subprocess.CalledProcessError: If the 'update-grub' command fails or returns a non-zero
        exit status.
    """

    # fix grub timeout
    with open('/etc/default/grub', 'r') as file:
        text = file.readlines()

    for i, line in enumerate(text):
        if 'GRUB_TIMEOUT' in line:
            text[i] = line.replace('5', '0')
            break

    with open('/etc/default/grub', 'w') as file:
        file.writelines(text)

    update-grub = shutil.which('update-grub')
    bash(f'{update-grub}')

def main(args):
    def main(args):
    """
    Sets up a fresh Debian installation to a known configuration by executing several configuration
    tasks, such as updating the system, configuring the hostname, setting up environment variables,
    modifying the user, and fixing the GRUB timeout. This function takes no arguments, and returns 0
    upon successful completion.

    Args:
        args (list): A list of command-line arguments. This parameter is unused in this function.

    Returns:
        int: The exit code of the program. Returns 0 upon successful completion.
    """

    if os.geteuid() != 0:
        print("This script must be run as a privileged user or with the sudo command.")
        exit(1)

    user = quote('phil')

    try:
        pwd.getpwname(user)
    except KeyError:
        useradd = shutil.which('useradd')
        bash(f'{useradd} -m -s /bin/bash {user}')

    update()
    networkinterface()
    hostname()
    envvar()
    setupuser(user)
    grub()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
