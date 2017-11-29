"""
Simple class to manage system authentication through PAM
"""

from pam import pam
from app import app

if 'USERS' in app.config:
    ALLOWED_USERS = app.config['USERS']
else:
    ALLOWED_USERS = None

class SystemAuth(object):
    """
    Rely on PAM for system authentication verification
    """

    auth_service = 'login'

    def __init__(self):
        self.auth = pam()
        self.service = self.__class__.auth_service

    def authenticate(self, user, pwd):
        """
        Use PAM module to verify credentials against system
        """
        if ALLOWED_USERS and user in ALLOWED_USERS:
            return self.auth.authenticate(user, pwd, service=self.service)
        return False

    def change_service(self, new_service):
        """
        Change to another PAM service (no validation performed)
        """
        self.service = new_service
