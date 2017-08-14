A web application (Flask) for pybinder

Note: As of this writing, you cannot rely on the pam module obtained via pip3 - it is out of date. Instead, download and install
from source (github): https://github.com/FirefighterBlu3/python-pam
[To install, 'git clone <URL>' and 'sudo python3 setup.py install']


The application needs to be run as root, in order for authentication of system users to work. When running in non-privileged mode, say by user X, only user X will be able to authenticate through the website/API.
