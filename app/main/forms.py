from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, \
    RadioField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
from app.models import User

#Forms for manipulating Budget_Category and Budget_History objects
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

#Forms for manipulating Transaction objects
class InputTransactionForm(FlaskForm):

    submit = SubmitField("Submit Transaction")

class EditTransactionForm(FlaskForm):

    submit = SubmitField("Submit Transaction Changes")

class DeleteTransactionForm(FlaskForm):

    submit = SubmitField("Delete Transaction")