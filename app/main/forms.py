from app.models import User
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, \
    RadioField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, NoneOf

###################################################################
#Forms for manipulating Budget_Category and Budget_History objects#
###################################################################

class AddBudgetForm(FlaskForm):
    category_title = StringField('Category Title', validators=[DataRequired()])
    current_balance = DecimalField('Current Balance', validators=[Optional()])
    target_period = SelectField('Budget Period',validators=[DataRequired()], choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[DataRequired()])

    submit = SubmitField("Submit Budget")

class EditBudgetForm(FlaskForm):

    select_budget = RadioField('Select Budget', choices=[], validators=[DataRequired()], coerce=int)

    category_title = StringField('Category Title', validators=[Optional()])
    current_balance = DecimalField('Current Balance', validators=[Optional()])
    target_period = SelectField('Budget Period',choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[Optional()])

    submit = SubmitField("Submit Budget Changes")

class DeleteBudgetForm(FlaskForm):

    select_budget = RadioField('Select Budget', choices=[], validators=[DataRequired()], coerce=int)
    delete_or_end_budget = RadioField('Delete or End?', choices=[(1,'Delete'),(2,'End')], validators=[DataRequired()], coerce=int)

    submit = SubmitField("Delete or End Category")

############################################
#Forms for manipulating Transaction objects#
############################################

class AddTransactionForm(FlaskForm):
    # TODO: display the date in form as local date, not UTC.
    trans_date = DateField('Date',validators=[Optional()],format='%Y-%m-%d',render_kw={'placeholder':'YYYY-MM-DD'})
    trans_type = SelectField('Type',validators=[DataRequired()],choices=[('E','Expense'),('I','Income')], coerce=str)
    trans_amount = DecimalField('Amount',validators=[DataRequired()])
    # TODO: figure out form validation with SelectField
    trans_category = SelectField('Budget Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_vendor = StringField('Vendor',validators=[Optional()])
    trans_note = StringField('Note',validators=[Optional()])
    submit = SubmitField("Submit Transaction")

class EditTransactionForm(FlaskForm):
    select_trans = RadioField('Select Transaction', choices=[], validators=[DataRequired()], coerce=int)

    trans_date = DateField('Date',validators=[Optional()],format='%Y-%m-%d',render_kw={'placeholder':'YYYY-MM-DD'})
    trans_amount = DecimalField('Amount',validators=[Optional()])
    trans_type = SelectField('Type',validators=[Optional()],choices=[('S','- Select Type -'),('E','Expense'),('I','Income')], coerce=str, default=None)
    # TODO: figure out form validation with SelectField
    trans_category = SelectField('Budget Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_vendor = StringField('Vendor',validators=[Optional()])
    trans_note = StringField('Note',validators=[Optional()])

    submit = SubmitField("Submit Transaction Changes")

class DeleteTransactionForm(FlaskForm): 
    select_trans = RadioField('Select Transaction', choices=[], validators=[DataRequired()], coerce=int)

    submit = SubmitField("Delete Transaction")

class TransferForm(FlaskForm):
    from_category = SelectField('From Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    to_category = SelectField('To Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_amount = DecimalField('Amount',validators=[Optional()])
    submit = SubmitField("Submit Transfer")
