# pylint: disable=missing-docstring

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search_terms = StringField('Search Entries:', validators=[DataRequired()])

class AddForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    ipaddr = StringField('Address:', validators=[DataRequired()])

class DeleteForm(FlaskForm):
    entry = StringField('Entry:', validators=[DataRequired()])

class AliasForm(FlaskForm):
    alias = StringField('Alias:', validators=[DataRequired()])
    real_name = StringField('Real Name:', validators=[DataRequired()])

class RangeAddForm(AddForm):
    num = IntegerField('Number of entries:', validators=[DataRequired()])
    start_index = StringField('Starting Index (optional):')

class RangeDeleteForm(DeleteForm):
    num = IntegerField('Number of entries:', validators=[DataRequired()])
