import os, sys
# Assumes that pybinder is a sibling folder (same parent). Adjust accordingly.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)
from searchdns import SearchDNS
from managedns import ManageDNS, ManageDNSError
from modifydns import parse_key_file

# This items should be placed in a config file
server = "129.40.40.21"
forward_zone = "pbm.ihost.com"
reverse_zone = "40.129.in-addr.arpa"
searcher = SearchDNS(server, forward_zone)
