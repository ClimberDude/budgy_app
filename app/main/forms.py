from app.models import User
from datetime import datetime
# from flask_login import current_user
from flask_security import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, \
    RadioField, SelectField, FieldList, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, NoneOf

###################################################################
#Forms for manipulating Budget_Category and Budget_History objects#
###################################################################

class AddBudgetForm(FlaskForm):
    category_title = StringField('Category Title', validators=[DataRequired()])
    spending_category = StringField('Spending Category', validators=[DataRequired()])
    current_balance = DecimalField('Current Balance', validators=[Optional()])
    target_period = SelectField('Budget Period',validators=[DataRequired()], choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[DataRequired()])

    submit = SubmitField("Submit Budget")

    def validate_category_title(self, category_title):
        title = current_user.budget_categories.filter_by(category_title=category_title.data).first()
        if title is not None:
            raise ValidationError('Please use a different Category Title.')


class AddBatchBudgetForm(FlaskForm):
    budget_csv_file = FileField('CSV File',validators=[FileRequired(),FileAllowed(['csv'],'Only CSV files are accepted.')])
    submit_batch = SubmitField("Submit Budget File")

class EditBudgetForm(FlaskForm):

    select_budget = RadioField('Select Budget', choices=[], validators=[DataRequired()], coerce=int)

    category_title = StringField('Category Title', validators=[Optional()])
    spending_category = StringField('Spending Category', validators=[Optional()])
    current_balance = DecimalField('Current Balance', validators=[Optional()])
    target_period = SelectField('Budget Period',choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[Optional()])

    submit = SubmitField("Submit Changes")

class DeleteBudgetForm(FlaskForm):

    select_budget = RadioField('Select Budget', choices=[], validators=[DataRequired()], coerce=int)
    delete_or_end_budget = RadioField('Delete or End?', choices=[(1,'Delete'),(2,'End')], validators=[DataRequired()], coerce=int)

    submit = SubmitField("Delete or End Category")

class FundBudgetEntryForm(FlaskForm):
    fund_value = DecimalField(id="fund",validators=[Optional()])

class FundingForm(FlaskForm):
    unallocated_income = DecimalField(id="entry",validators=[Optional()])
    fund_budgets = FieldList(FormField(FundBudgetEntryForm),validators=[Optional()],min_entries=1)
    submit = SubmitField("Submit Funding Allotments")


############################################
#Forms for manipulating Transaction objects#
############################################

class AddTransactionForm(FlaskForm):
    trans_date = DateField('Date',validators=[Optional()],format='%Y-%m-%d')#,render_kw={'placeholder':'YYYY-MM-DD'})
    trans_type = SelectField('Type',validators=[Optional()],choices=[('E','Expense'),('I','Income')], coerce=str)
    trans_amount = DecimalField('Amount',validators=[DataRequired()])
    # TODO: figure out form validation with SelectField
    trans_category = SelectField('Budget Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_vendor = StringField('Vendor',validators=[Optional()])
    trans_note = StringField('Note',validators=[Optional()])
    submit = SubmitField("Submit Transaction")

class AddBatchTransactionForm(FlaskForm):
    trans_csv_file = FileField('CSV File',validators=[FileRequired(),FileAllowed(['csv'],'Only CSV files are accepted.')])
    submit_batch = SubmitField("Submit Trans. File")


class EditTransactionForm(FlaskForm):
    select_trans = RadioField('Select Transaction', choices=[], validators=[Optional()], coerce=int)

    trans_date = DateField('Date',validators=[Optional()],format='%Y-%m-%d',render_kw={'placeholder':'YYYY-MM-DD'})
    trans_amount = DecimalField('Amount',validators=[Optional()])
    trans_type = SelectField('Type',validators=[Optional()],choices=[('S','- Select Type -'),('E','Expense'),('I','Income')], coerce=str, default=None)
    # TODO: figure out form validation with SelectField
    trans_category = SelectField('Budget Category',validators=[Optional()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_vendor = StringField('Vendor',validators=[Optional()])
    trans_note = StringField('Note',validators=[Optional()])

    submit = SubmitField("Submit Trans. Edits")

class DeleteTransactionForm(FlaskForm): 
    select_trans = RadioField('Select Transaction', choices=[], validators=[Optional()], coerce=int)

    submit = SubmitField("Delete Transaction")

class TransferForm(FlaskForm):
    from_category = SelectField('From Category',validators=[DataRequired()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    to_category = SelectField('To Category',validators=[DataRequired()],choices=[(0,'- Select Category -')],default=0,coerce=int)
    trans_amount = DecimalField('Amount',validators=[DataRequired()])
    submit = SubmitField("Submit Transfer")
