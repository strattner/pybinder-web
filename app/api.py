"""
Collection of Flask-RESTFul Resources
"""

import ipaddress
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse
from .functions import searcher, manager
from .auth import SystemAuth
from managedns import ManageDNSError
from app import app

http_auth = HTTPBasicAuth()
system_auth = SystemAuth()

FORWARD_ZONE = app.config['FORWARD_ZONE']
if 'ALLOWED_DOMAINS' in app.config:
    ALLOWED_DOMAINS = app.config['ALLOWED_DOMAINS'].split(',')
else:
    ALLOWED_DOMAINS = None

if 'SUBNETS' in app.config:
    SUBNETS = [ipaddress.ip_network(x) for x in app.config['SUBNETS']]
else:
    SUBNETS = None

def name_allowed(name):
    """ Return true if name is within the allowed domain list """
    if not ALLOWED_DOMAINS:
        return True
    if '.' in name:
        [hostname, domain] = name.split('.', 1)
    else:
        return True
    if domain in ALLOWED_DOMAINS or domain == FORWARD_ZONE:
        return True
    return False

def address_allowed(ip):
    """ Return true if IP address is within the allowed subnet list """
    if not SUBNETS:
        return True
    ip = ipaddress.ip_address(ip)
    for sub in SUBNETS:
        if ip in sub:
            return True
    return False

def is_address(entry):
    """ Checks if entry is a valid IP address """
    try:
        _ = ipaddress.ip_ipaddress(entry)
    except ValueError:
        return False
    return True

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
            if not name_allowed(name):
                raise ValueError("Not authorized to add " + name)
            for addr in ip:
                if not address_allowed(addr):
                    raise ValueError("Not authorized to add " + addr)
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
            if not name_allowed(alias):
                raise ValueError("Not authorized to add " + alias)
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
            if is_address(entry):
                if not address_allowed(entry):
                    raise ValueError("Not authorized to delete " + entry)
            else:
                if not name_allowed(entry):
                    raise ValueError("Not authorized to delete " + entry)
            answer = manager.delete_record(entry)
            answer = [str(a) for a in answer]
        except (ManageDNSError, ValueError) as mde:
            return {'message': 'Error: ' + str(mde)}, 400
        return {'message': str(answer)}
