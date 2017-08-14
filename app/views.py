"""
pybinder-web

Flask application to provide a web interface to manage DNS (using pybinder).

Author: Scott Strattner (sstrattn@us.ibm.com)

Copyright (c) 2017 IBM Corp.
"""

# PyLint treats any variable outside of a function as a constant (instead
# of a global variable). Disabling this check.
# pylint: disable=invalid-name

import os
import sys
from collections import OrderedDict
from flask import render_template
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from app import app
from .forms import AddForm, AliasForm, DeleteForm, RangeAddForm, RangeDeleteForm, SearchForm
from .functions import forward_zone, searcher, create_manager
from .api import SearchRecord, AddAlias, AddRecord, DeleteRecord, ReplaceAlias, ReplaceRecord 
from .auth import SystemAuth

# Need to add path for pybinder
# Assumes that pybinder is a sibling folder (same parent). Adjust if necessary.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)
from managedns import ManageDNS, ManageDNSError
from modifydns import parse_key_file

# Enable Flask-RESTful API and add endpoints and resources
api = Api(app)
api.add_resource(SearchRecord, '/api/search/<entry>')
api.add_resource(AddAlias, '/api/add_alias')
api.add_resource(AddRecord, '/api/add')
api.add_resource(DeleteRecord, '/api/delete/<entry>')
api.add_resource(ReplaceAlias, '/api/replace_alias')
api.add_resource(ReplaceRecord, '/api/replace')

# Global variable declarations
http_auth = HTTPBasicAuth()
system_auth = SystemAuth()

# These items should be placed in a config file
server = "129.40.40.21"
forward_zone = "pbm.ihost.com"
reverse_zone = "40.129.in-addr.arpa"
ddns_key = "../pybinder/ddns-test.key"
dns_manager = {}

@http_auth.verify_password
def verify_pwd(user, pwd):
    """
    This works, so long as the system relies on local auth (not some custom PAM module)
    """
    return system_auth.authenticate(user, pwd)

@app.route('/')
@app.route('/index')
def index():
    """
    Home page, should show any important messages, links to help, etc.
    """
    return render_template('index.html', title='Home', user=http_auth.username())

@app.route('/search/<name_or_address>')
def search_specific(name_or_address):
    """
    Allows for direct searches through the URL (not the same as the API)
    """
    user = http_auth.username()
    answer = {}
    answer[name_or_address] = str(searcher.query(name_or_address)).split(' ', 1)[1]
    return render_template('search_results.html', title='Search', answer=answer, user=user)

@app.route('/search', methods=['GET', 'POST'])
def search_main():
    """
    Main search method. It is not required to authenticate to access search,
    but user identity is retrieved so that it can show up on the page.
    """
    form = SearchForm()
    user = http_auth.username()
    if form.validate_on_submit():
        query_terms = form.search_terms.data.split(' ')
        answer = OrderedDict()
        for query in query_terms:
            result = str(searcher.query(query))
            answer[query] = result.split(' ', 1)[1]
        return render_template('search_results.html', title='Search', answer=answer, user=user)
    return render_template('search.html', title='Search', zone=forward_zone, form=form, user=user)

@app.route('/add', methods=['GET', 'POST'])
@http_auth.login_required
def add_main(force=False, title='Add'):
    """
    Main add method.
    """
    form = AddForm()
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        name = form.name.data
        ipaddr = form.ipaddr.data.split(' ')
        try:
            answer = dns_manager[user].add_record(name, ipaddr, force)
        except (ManageDNSError, ValueError) as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title=title, answer=answer, user=user)
    return render_template('add.html', title=title, force=force,
                           zone=forward_zone, user=user, form=form)

@app.route('/alias', methods=['GET', 'POST'])
@http_auth.login_required
def add_alias(force=False, title='Add Alias'):
    """
    Main (and only) alias method. No current implementation of 'replace alias',
    and no need for a range function.
    """
    form = AliasForm()
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        alias = form.alias.data
        real_name = form.real_name.data
        try:
            answer = dns_manager[user].add_alias(alias, real_name, force)
        except (ManageDNSError, ValueError) as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title=title, answer=answer, user=user)
    return render_template('alias.html', title=title, force=force,
                           zone=forward_zone, user=user, form=form)

@app.route('/range-add', methods=['GET', 'POST'])
@http_auth.login_required
def add_range(force=False, title='Range Add'):
    """
    Add Range method
    """
    form = RangeAddForm()
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        name = form.name.data
        ipaddr = form.ipaddr.data
        num = form.num.data
        start_index = form.start_index.data
        try:
            answer = dns_manager[user].add_range(name, ipaddr, num, start_index, force)
        except (ManageDNSError, ValueError) as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title=title, answer=answer, user=user)
    return render_template('range-add.html', title=title, force=force,
                           zone=forward_zone, user=user, form=form)

@app.route('/replace', methods=['GET', 'POST'])
@http_auth.login_required
def replace_main():
    """
    Replace method - calls add_main with force=True
    """
    return add_main(True, 'Replace')

@app.route('/range-replace', methods=['GET', 'POST'])
@http_auth.login_required
def replace_range():
    """
    Replace Range method - calls add_range with force=True
    """
    return add_range(True, 'Range Replace')

@app.route('/delete', methods=['GET', 'POST'])
@http_auth.login_required
def delete_main():
    """
    Main delete method
    """
    form = DeleteForm()
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        entry = form.entry.data
        try:
            answer = dns_manager[user].delete_record(entry)
        except (ManageDNSError, ValueError) as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title='Delete', answer=answer, user=user)
    return render_template('delete.html', title='Delete', zone=forward_zone, user=user, form=form)

@app.route('/range-delete', methods=['GET', 'POST'])
@http_auth.login_required
def delete_range():
    """
    Delete range method (just to stop pylint from complaining)
    """
    form = RangeDeleteForm()
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    if form.validate_on_submit():
        entry = form.entry.data
        num = form.num.data
        try:
            answer = dns_manager[user].delete_range(entry, num)
        except (ManageDNSError, ValueError) as mde:
            return render_template('errors.html', title='Error', error=[mde], user=user)
        return render_template('results.html', title='Range Delete', answer=answer, user=user)
    return render_template('range-delete.html', title='Range Delete', zone=forward_zone,
                           user=user, form=form)

@app.route('/history')
@http_auth.login_required
def history():
    """
    Return user history (reversed, most recent first)
    """
    user = http_auth.username()
    if user not in dns_manager:
        dns_manager[user] = create_manager(user)
    user_history = dns_manager[user].get_history()
    if user_history:
        user_history = reversed(user_history)
    return render_template('history.html', title='History', history=user_history, user=user)

@app.route('/clear-history', methods=['POST'])
@http_auth.login_required
def clear_history():
    """
    Clear user history
    """
    user = http_auth.username()
    if user in dns_manager:
        dns_manager[user].clear_history()
    user_history = dns_manager[user].get_history()
    return render_template('history.html', title='History', history=user_history, user=user)
