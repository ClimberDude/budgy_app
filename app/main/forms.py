from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, \
    RadioField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
from app.models import User

#Forms for manipulating Budget_Category and Budget_History objects
class InputBudgetForm(FlaskForm):
    category_title = StringField('Category Title', validators=[DataRequired()])
    current_balance = DecimalField('Current Balance', validators=[])

    target_period = SelectField('Budget Period',choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[DataRequired()])

    submit = SubmitField("Submit Budget")

class EditBudgetForm(FlaskForm):

    select_budget = RadioField('Select Budget', choices=[], validators=[DataRequired()], coerce=int)

    category_title = StringField('Category Title', validators=[Optional()])
    current_balance = DecimalField('Current Balance', validators=[Optional()])

    target_period = SelectField('Budget Period',choices=[(1,'Bi-Weekly'),(2,'Monthly'),(3,'Annual')],coerce=int)
    target_value = DecimalField("Budget Target",validators=[Optional()])

    submit = SubmitField("Submit Budget Changes")

class EndBudgetForm(FlaskForm):

    submit = SubmitField("End Category and Transfer Balance")

class DeleteBudgetForm(FlaskForm):

    submit = SubmitField("Permanently Delete Budget Category")

#Forms for manipulating Transaction objects
class InputTransactionForm(FlaskForm):

    submit = SubmitField("Submit Transaction")

class EditTransactionForm(FlaskForm):

    submit = SubmitField("Submit Transaction Changes")

class DeleteTransactionForm(FlaskForm):

    submit = SubmitField("Delete Transaction")