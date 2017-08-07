import os, sys
# Assumes that pybinder is a sibling folder (same parent). Adjust accordingly.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)
from searchdns import SearchDNS
from managedns import ManageDNS
from modifydns import parse_key_file

# This items should be placed in a config file
server = "129.40.40.21"
forward_zone = "pbm.ihost.com"
reverse_zone = "40.129.in-addr.arpa"
searcher = SearchDNS(server, forward_zone)
ddns_key = "../pybinder/ddns-test.key"

if os.path.isfile(ddns_key):
    key_name, key_hash = parse_key_file(ddns_key)
else:
    key_name, key_hash = (None, None)

def create_manager(user):
    """
    Return a ManageDNS object associated with user (for history)
    """
    return ManageDNS(nameserver=server, forward_zone=forward_zone,
                     reverse_zone=reverse_zone, user=user, key_name=key_name, key_hash=key_hash)


# A userless manager is used for API calls
manager = create_manager(None)

