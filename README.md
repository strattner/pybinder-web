# pybinder-web

A web application (Flask) for pybinder

## Getting Started

### Prerequisites

On a vanilla Ubuntu 16.04 system, the following need to be installed:

__**General Requirements**__
Python 3.5 *apt-get install python3*
pip3 *apt-get install python3-pip* [to install the Python modules]
git *apt-get install git* [to obtain pybinder and this application]

__**Pybinder Requirements**__
pybinder *git clone https://github.ibm.com/sstrattn/pybinder.git*
dnspython *pip3 install dnspython*
docopt *pip3 install docopt*

Note: As of this writing, you cannot rely on the pam module obtained via pip3 - it is out of date.
Instead, download and install from source: https://github.com/FirefighterBlu3/python-pam
[To install, 'git clone <URL>' 'cd python-pam' 'sudo python3 setup.py install']

### Installing

First, follow the install instructions for [pybinder](https://https://github.ibm.com/sstrattn/pybinder). Use the pybinder CLI tools to search, add, and
remove DNS entries to ensure your system is set up correctly and able to communicate with the DNS
server. To make changes you will need a crypto key - with named.conf configured appropriately - to
authenticate and manage the zone files.

Assuming your pybinder install is working correctly...

Grab the pybinder-web source from git

```
git clone https://github.ibm.com/sstrattn/pybinder-web.git
```

## Deployment

The application needs to be run as root, in order for authentication of system users to work. When running in non-privileged mode, say by user X, only user X will be able to authenticate through the website/API.

```
cd pybinder-web
sudo python3 ./run.py
```

Edit run.py to change the port Flask listens on (defaults to 5353).
