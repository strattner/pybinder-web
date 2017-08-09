"""
Collection of Flask-RESTFul Resources
"""

import ipaddress
from flask_httpauth import HTTPBasicAuth
from flask_restful import abort, Resource, reqparse
from .functions import searcher, manager
from .auth import SystemAuth
from managedns import ManageDNSError

http_auth = HTTPBasicAuth()
system_auth = SystemAuth()

@http_auth.verify_password
def verify_pwd(user, pwd):
    """
    This works, so long as the system relies on local auth (not some custom PAM module)
    """
    return system_auth.authenticate(user, pwd)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class SearchRecord(Resource):
    def get(self, entry):
        return {entry: str(searcher.query(entry)).split(' ', 1)[1]}

class AddRecord(Resource):

    decorators = [http_auth.login_required]

    def __init__(self):
        super()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='Hostname or FQDN', required=True)
        self.parser.add_argument('address', type=str, help='IP address', required=True)

    def post(self, force=False):
        args = self.parser.parse_args()
        name = args['name']
        ipaddr = args['address']
        try:
            ip = ipaddress.ip_address(ipaddr)
            answer = manager.add_record(name, str(ip), force)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return { 'message': 'Error: ' + str(mde) }, 400
        return { 'message': str(answer) }

class ReplaceRecord(AddRecord):

    def put(self):
        return self.post(force=True)

class DeleteRecord(Resource):

    decorators = [http_auth.login_required]

    def delete(self, entry):
        try:
            answer = manager.delete_record(entry)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return { 'message': 'Error: ' + str(mde) }, 400
        return { 'message': str(answer) }
