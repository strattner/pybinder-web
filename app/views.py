import os
import sys
from collections import OrderedDict
from pam import pam
from flask import render_template
from flask_httpauth import HTTPBasicAuth
from app import app
from .forms import AddForm, DeleteForm, SearchForm

class SystemAuth(object):
    """
    Rely on PAM for system authentication verification
    """

    def __init__(self):
        self.auth = pam()

    def authenticate(self, user, pwd):
        return self.auth.authenticate(user, pwd, service='login')

auth = HTTPBasicAuth()
system_auth = SystemAuth()

# Assumes that pybinder is a sibling folder (same parent). Adjust if necessary.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)

from searchdns import SearchDNS
from managedns import ManageDNS, ManageDNSError
from modifydns import parse_key_file

server = "129.40.40.21"
forward_zone = "pbm.ihost.com"
reverse_zone = "40.129.in-addr.arpa"
searcher = SearchDNS(server, forward_zone)
ddns_key = "../pybinder/ddns-test.key"
dns_manager = {}

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

@auth.verify_password
def verify_pwd(user, pwd):
    return system_auth.authenticate(user, pwd)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user=auth.username())

@app.route('/search/<name_or_address>')
def search_specific(name_or_address):
    user = auth.username()
    answer = {}
    answer[name_or_address] = str(searcher.query(name_or_address)).split(' ', 1)[1]
    return render_template('search_results.html', title='Search', answer=answer, user=user)

@app.route('/search', methods=['GET', 'POST'])
def search_main():
    form = SearchForm()
    user = auth.username()
    if form.validate_on_submit():
        query_terms = form.search_terms.data.split(' ')
        answer = OrderedDict()
        for query in query_terms:
            result = str(searcher.query(query))
            answer[query] = result.split(' ', 1)[1]
        return render_template('search_results.html', title='Search', answer=answer, user=user)
    return render_template('search.html', title='Search', zone=forward_zone, form=form, user=user)

@app.route('/add', methods=['GET', 'POST'])
@auth.login_required
def add_main(force=False, title='Add'):
    form = AddForm()
    user = auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        name = form.name.data
        ipaddr = form.ipaddr.data.split(' ')
        try:
            answer = dns_manager[user].add_record(name, ipaddr, force)
        except ManageDNSError as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title=title, answer=answer, user=user)
    return render_template('add.html', title=title, force=force,
                           zone=forward_zone, user=user, form=form)

@app.route('/replace', methods=['GET', 'POST'])
@auth.login_required
def replace_main():
    return add_main(True, 'Replace')

@app.route('/delete', methods=['GET', 'POST'])
@auth.login_required
def delete_main():
    form = DeleteForm()
    user = auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        entry = form.entry.data
        try:
            answer = dns_manager[user].delete_record(entry)
        except ManageDNSError as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title='Delete', answer=answer, user=user)
    return render_template('delete.html', title='Delete', zone=forward_zone, user=user, form=form)

@app.route('/history')
@auth.login_required
def history():
    user = auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    history = dns_manager[user].get_history()
    if history:
        history = reversed(history)
    return render_template('history.html', title='History', history=history, user=user)

@app.route('/clear-history', methods=['POST'])
@auth.login_required
def clear_history():
    user = auth.username()
    if user in dns_manager:
        dns_manager[user].clear_history()
    history = dns_manager[user].get_history()
    return render_template('history.html', title='History', history=history, user=user)
