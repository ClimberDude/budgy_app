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

class SummaryVisForm(FlaskForm):
    start_month = SelectField('Starting Month',
        validators=[DataRequired()],
        choices=[(1,'Jan'),(2,'Feb'),(3,'Mar'),(4,'Apr'),(5,'May'),(6,'Jun'),\
            (7,'Jul'),(8,'Aug'),(9,'Sep'),(10,'Oct'),(11,'Nov'),(12,'Dec')],
        coerce=int)
    start_year = SelectField('Starting Year',
        validators=[DataRequired()],
        choices=[],
        coerce=int)
    span = SelectField('Span',
        validators=[DataRequired()],
        choices=[(1,'1 month'),(2,'2 months'),(3,'3 months'),(4,'4 months'),(5,'5 months'),(6,'6 months'),\
            (7,'7 months'),(8,'8 months'),(9,'9 months'),(10,'10 months'),(11,'11 months'),(12,'12 months')],
        default=3,
        coerce=int)
    prior_or_following = RadioField('',choices=[(0,"Prior to Selection"),(1,"Following Selection")],
        validators=[Optional()],
        default=0,
        coerce=int)
    update = SubmitField('Update Table')

