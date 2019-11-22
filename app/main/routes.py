from app import db
from app.main import bp
from app.main.forms import AddBudgetForm, EditBudgetForm, DeleteBudgetForm

from app.models import Budget_Category, Budget_History, Transaction

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/landing', methods=['GET', 'POST'])
def landing():
    return render_template('landing.html',
                            title='Landing Page')

@bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def budget_add():
    form=AddBudgetForm()
    if form.validate_on_submit():
        budget_category= Budget_Category(id_user = current_user.id,
                                         category_title = form.category_title.data,
                                         current_balance = form.current_balance.data)

        db.session.add(budget_category)
        db.session.commit()

        if form.target_period.data == 1:
            annual_budget = form.target_value.data * 26
        elif form.target_period.data == 2:
            annual_budget = form.target_value.data * 12
        else:
            annual_budget = form.target_value.data

        budget_history = Budget_History(id_user = current_user.id,
                                        id_budget_category = budget_category.id,
                                        start_datetime = datetime.utcnow(),
                                        status = 'C',
                                        annual_budget = annual_budget)

        db.session.add(budget_history)
        db.session.commit()

        flash('Category {} has been added.'.format(budget_category.category_title))
        return redirect(url_for('main.budget_add'))

    return render_template('budgets/input.html',
                           title='Add Budget',
                           form=form)

@bp.route('/budget/edit', methods=['GET', 'POST'])
@login_required
def budget_edit():
    #Populate the list of radio button choices with the current list of
    #budget categories
    radio_choices = [(c.id,c.category_title) for c in current_user.budget_categories.order_by(Budget_Category.category_title).all()]

    #Pull all the current data for the categories for the current user, to display
    budget_categories = current_user.budget_categories.order_by(Budget_Category.category_title).all()

    #Instantiate the form
    form = EditBudgetForm()

    #Pass dynamic radio button data to the form
    form.select_budget.choices = radio_choices

    #If the form passes the built in validators, move on
    if form.validate_on_submit():
        #Identify the category to be edited by pulling the data from the radio selection
        category = current_user.budget_categories.filter_by(id=form.select_budget.data).first()

        #Check each form field to see if new data has been entered to supercede old data
        #Any or all data can be entered, so individual if statements are used.
        if form.category_title.data:
            if form.category_title.data == category.category_title:
                flash("The category title you've entered matches your old title!")
            else:
                category.category_title = form.category_title.data
                flash("The category title has been changed.")

        if form.current_balance.data:
            if form.current_balance.data == category.current_balance:
                flash("The current balance you've entered matches your old balance!")
            else:
                category.current_balance = form.current_balance.data
                flash("The current balance has been changed.")

        #Both target period and target value are required to update the budget amount
        if form.target_period.data and form.target_value.data:
            #If new budget amounts are entered, the data needs to be updated in
            #the Budget_History table linked to the Budget_Category table

            #First, pull the current (now obsoleted) budget history for the
            #current budget category
            obsolete_history = category.budget_history.filter_by(status='C').first()

            #Now check that a change to the annual budget has actually been made
            if form.target_period.data == 1:
                annual_budget = form.target_value.data * 26
            elif form.target_period.data == 2:
                annual_budget = form.target_value.data * 12
            else:
                annual_budget = form.target_value.data

            if obsolete_history.annual_budget == annual_budget:
                flash("The new budget you've entered matches your old budget!")
            else:
                #if the obsoleted budget doesn't equal the new value, proceed with
                #the edit.

                #Populate the obsoleteing information
                obsolete_history.end_datetime = datetime.utcnow()
                obsolete_history.status = 'O'

                #Next, create the new budget history entry from the entered form data
                current_history = Budget_History(id_user = current_user.id,
                                                 id_budget_category = category.id,
                                                 start_datetime = datetime.utcnow(),
                                                 status = 'C',
                                                 annual_budget = annual_budget)

                #add the new history object to the database
                db.session.add(current_history)

                flash("Your annual budget target has been changed.")
        #push all changes through to the database
        db.session.commit()

        #reload the edit page for further edits
        return redirect(url_for('main.budget_edit'))

    return render_template('budgets/edit.html',
                            title='edit_budget',
                           form=form,
                           budget_categories=budget_categories)

@bp.route('/budget/delete', methods=['GET','POST'])
@login_required
def budget_delete():

    #Populate the list of radio button choices with the current list of
    #budget categories
    radio_choices = [(c.id,c.category_title) for c in current_user.budget_categories.order_by(Budget_Category.category_title).all()]

    #Pull all the current data for the categories for the current user, to display
    budget_categories = current_user.budget_categories.order_by(Budget_Category.category_title).all()

    #Instantiate the form
    form = DeleteBudgetForm()

    #Pass dynamic radio button data to the form
    form.select_budget.choices = radio_choices

    if form.validate_on_submit():
        #Identify the category to be edited by pulling the data from the radio selection
        category = current_user.budget_categories.filter_by(id=form.select_budget.data).first()

        #Pull the user selection of whether to delete or end the category
        delete_or_end=form.delete_or_end_budget.data

        if delete_or_end == 1:
            #Delete budget category
            # TODO: remove any applicable budget history table entries along with the 
            #   budget category data. Look into adding cascading delete to the relationship in db model.
            db.session.delete(category)
            db.session.commit()

            flash('The category has been deleted.')
            return redirect(url_for('main.budget_delete'))
        elif delete_or_end == 2:
            # TODO: implement the end functionality once the database table has been updated to accept 
            #   a status character.

            flash("Ending a category is not yet implemented.")
            return redirect(url_for('main.budget_delete'))

    return render_template('budgets/delete.html',
                            title='Delete/End Budget',
                            form=form,
                            budget_categories=budget_categories)