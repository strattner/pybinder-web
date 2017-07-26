"""
Collection of Flask-RESTFul Resources
"""

from flask_restful import Resource
from .functions import searcher

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class SearchRecord(Resource):
    def get(self, entry):
        return {entry: str(searcher.query(entry)).split(' ', 1)[1]}
