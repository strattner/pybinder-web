import os, sys
from collections import OrderedDict
from pam import pam
from flask import render_template
from flask_basicauth import BasicAuth
from app import app
from .forms import SearchForm

class SystemAuth(BasicAuth):
    """
    Overriding BasicAuth to provide PAM-based authentication
    checking.
    """

    @staticmethod
    def check_credentials(username, password):
        """
        Checks user and pwd against system
        """
        system_auth = pam()
        return system_auth.authenticate(username, password, service='login')

basic_auth = SystemAuth(app)

# Assumes that pybinder is a sibling folder (same parent). Adjust if necessary.
pybinder_path = os.path.abspath(os.path.join('..', 'pybinder'))
sys.path.append(pybinder_path)

from searchdns import SearchDNS

server = "129.40.40.21"
forward_zone = "pbm.ihost.com"
reverse_zone = "40.129.in-addr.arpa"
searcher = SearchDNS(server, forward_zone)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/search/<name_or_address>')
def search_specific(name_or_address):
    return str(searcher.query(name_or_address))

@app.route('/search', methods=['GET', 'POST'])
def search_main():
    form = SearchForm()
    if form.validate_on_submit():
        query_terms = form.search_terms.data.split(' ')
        answer = OrderedDict()
        for query in query_terms:
            result = str(searcher.query(query))
            answer[query] = result.split(' ',1)[1]
        return render_template('search_results.html', answer=answer)
    return render_template('search.html', title='Search', zone=forward_zone, form=form)

@app.route('/add', methods=['GET', 'POST'])
@basic_auth.required
def add_main():
    return render_template('add.html')
