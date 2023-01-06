k8s-debian
============
set up debian on a fresh debian 11 server

# Warning: This is a work in progress and should not be used in production!

# Prerequisits
* fresh install of debian 11 server
* no swap on your servers
* one user account that will join the sudo group

# Setup
Download git and clone this repository
```bash
 # apt update && apt install git
```

Become non-privilaged user
```bash
 # su <user>
 $ cd
```

Pull this repo
```bash
 $ git clone https://github.com/poshaw/k8s-debian.git
 $ cd k8s-debian
```

You need to run the following as root
```bash
 $ exit
 # ./2-root-setup-debian.py
```
