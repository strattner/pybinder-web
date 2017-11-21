"""
Collection of Flask-RESTFul Resources
"""

import ipaddress
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse
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

class SearchRecord(Resource):
    """ Represent a search query and result """
    def get(self, entry):
        """ Return search result from get request """
        return {entry: str(searcher.query(entry)).split(' ', 1)[1]}

class AddRecord(Resource):
    """ Represent an A and PTR add """
    decorators = [http_auth.login_required]

    def __init__(self):
        super()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='Hostname or FQDN', required=True)
        self.parser.add_argument('address', type=str, help='IP address', required=True)

    def post(self, force=False):
        """ Add record from post request """
        args = self.parser.parse_args()
        name = args['name']
        ip = args['address'].split(' ')
        try:
            answer = manager.add_record(name, ip, force)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return {'message': 'Error: ' + str(mde)}, 400
        return {'message': str(answer)}

class AddAlias(Resource):
    """ Represent a CNAME add """
    decorators = [http_auth.login_required]

    def __init__(self):
        super()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('alias', type=str, help='Hostname or FQDN', required=True)
        self.parser.add_argument('real_name', type=str, help='Hostname or FQDN', required=True)

    def post(self, force=False):
        """ Add alias from post request """
        args = self.parser.parse_args()
        alias = args['alias']
        real_name = args['real_name']
        try:
            answer = manager.add_alias(alias, real_name, force)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return {'message': 'Error: ' + str(mde)}, 400
        return {'message': str(answer)}

class ReplaceRecord(AddRecord):
    """ Represent an A and PTR add/replace """

    def post(self, force=True):
        """ Add record from post request """
        return super(ReplaceRecord, self).post(force)

class DeleteRecord(Resource):
    """ Represent removal of A (and PTR) or CNAME """
    decorators = [http_auth.login_required]

    def delete(self, entry):
        """ Remove record from delete request """
        try:
            answer = manager.delete_record(entry)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return {'message': 'Error: ' + str(mde)}, 400
        return {'message': str(answer)}
