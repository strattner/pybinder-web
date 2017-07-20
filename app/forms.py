from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search_terms = StringField('Search Entries:', validators=[DataRequired()])

class AddForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    ipaddr = StringField('Address:', validators=[DataRequired()])
