from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../../config/pybinder-web.config')

from app import views

