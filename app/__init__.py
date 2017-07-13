from flask import Flask
from flask_basicauth import BasicAuth

# Insert the pam stuff here
class SystemAuth(BasicAuth):
    def check_credentials(username, password):
        pass

app = Flask(__name__)
app.config.from_object('config')

basic_auth = SystemAuth(app)

from app import views
