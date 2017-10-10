import os, sys
# Assumes that pybinder is a sibling folder (same parent). Adjust accordingly.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)
from searchdns import SearchDNS
from managedns import ManageDNS
from modifydns import parse_key_file

from app import app

if os.path.isfile(app.config['DDNS_KEY']):
    key_name, key_hash = parse_key_file(app.config['DDNS_KEY'])
else:
    key_name, key_hash = (None, None)

def create_manager(user):
    """
    Return a ManageDNS object associated with user (for history)
    """
    return ManageDNS(nameserver=app.config['SERVER'], forward_zone=app.config['FORWARD_ZONE'],
                     reverse_zone=app.config['REVERSE_ZONE'], user=user, key_name=key_name,
                     key_hash=key_hash)


# A userless manager is used for API calls
manager = create_manager(None)

# Searcher using FORWARD_ZONE
searcher = SearchDNS(nameserver=app.config['SERVER'], zone=app.config['FORWARD_ZONE'])
