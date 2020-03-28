from app.models import User
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, \
    RadioField, SelectField, FieldList, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, NoneOf

class IncomeVSpendingVisForm(FlaskForm):
    start_date = DateField('From',id='sdate',validators=[Optional()])
    end_date = DateField('To',id='edate',validators=[Optional()])
    budget = SelectField('Filter Budget Category',id='budget',validators=[Optional()],choices=[(0,'All Budget Categories')],default=0,coerce=int)
    category = SelectField('Filter Spending Category',id='spend',validators=[Optional()],choices=[('all','All Spending Categories')],default='all',coerce=str)
    update = SubmitField('Update Plot',id='update')

class SpendingByCategoryVisForm(FlaskForm):
    start_date = DateField('From',validators=[Optional()])
    end_date = DateField('To',validators=[Optional()])
    budget_or_spending = SelectField('Budget or Category',validators=[Optional()],choices=[(0,'Budget Categories'),(1,'Spending Categories')],default=0,coerce=int)
    update = SubmitField('Update Plot')
