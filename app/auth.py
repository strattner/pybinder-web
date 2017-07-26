"""
Simple class to manage system authentication through PAM
"""

from pam import pam

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
        return self.auth.authenticate(user, pwd, service=self.service)

    def change_service(self, new_service):
        """
        Change to another PAM service (no validation performed)
        """
        self.service = new_service
