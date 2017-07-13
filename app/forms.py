from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search_terms = StringField('search_terms', validators=[DataRequired()])
