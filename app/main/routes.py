from app import db
from app.main import bp
from app.main.forms import AddBudgetForm, EditBudgetForm, DeleteBudgetForm, \
                            AddTransactionForm, EditTransactionForm, DeleteTransactionForm

from app.models import Budget_Category, Budget_History, Transaction

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/landing', methods=['GET', 'POST'])
def landing():
    return render_template('landing.html',
                            title='Landing Page')

#route functions related to handling the budget categories
@bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def budget_add():
    budget_categories = current_user.budget_categories.order_by(Budget_Category.category_title).all()

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

    return render_template('budgets/add.html',
                           title='Add Budget',
                           form=form,
                           budget_categories=budget_categories)

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

@bp.route('/budget/view', methods=['GET','POST'])
@login_required
def budget_view():
    page = request.args.get('page',1,type=int)
    budgets = current_user.budget_categories.order_by(Budget_Category.category_title.asc()).paginate(page,
        10, False)

    next_url = url_for('main.budget_view', page=budgets.next_num) \
        if budgets.has_next else None
    prev_url = url_for('main.budget_view', page=budgets.prev_num) \
        if budgets.has_prev else None

    return render_template('budgets/view.html',
                            title='View Budgets',
                            budgets=budgets.items,
                            next_url=next_url,
                            prev_url=prev_url
                            )

#route functions related to handling transactions
@bp.route('/trans/add', methods=['GET','POST'])
@login_required
def trans_add():
    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.order_by(Budget_Category.category_title).all()]
    budget_categories = current_user.budget_categories.order_by(Budget_Category.category_title).all()

    form = AddTransactionForm()

    form.trans_category.choices += budget_choices

    if form.validate_on_submit():

        if form.trans_category.data == 0:
            flash('Please select a valid category')
            return redirect(url_for('main.trans_add'))

        transaction = Transaction(id_user = current_user.id,
                                    id_budget_category = form.trans_category.data,
                                    date = form.trans_date.data,
                                    amount = form.trans_amount.data,
                                    vendor = form.trans_vendor.data,
                                    note = form.trans_note.data,
                                    ttype = form.trans_type.data)
        
        db.session.add(transaction)
        db.session.commit()

        transaction.apply_transaction()

        flash("Your transaction has been added.")
        return redirect(url_for('main.trans_add'))

    return render_template('transactions/add.html',
                            title='Add Transactions',
                            form=form,
                            budget_categories=budget_categories,
                            )

@bp.route('/trans/edit', methods=['GET','POST'])
@login_required
def trans_edit():
    trans_choices = [(c.id,c.amount) for c in current_user.transactions.order_by(Transaction.date.desc()).all()]
    transactions = current_user.transactions.order_by(Transaction.date.desc()).all()
    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.order_by(Budget_Category.category_title).all()]

    form = EditTransactionForm() 
    form.select_trans.choices = trans_choices
    form.trans_category.choices += budget_choices

    if form.validate_on_submit():
        transaction = current_user.transactions.filter_by(id=form.select_trans.data).first()
        flash_note = []

        # TODO: figure out how to handle user and server date issues. How to get user timezone?
        if form.trans_date.data:
            if form.trans_date.data == transaction.date:
                flash("The new date you've entered matches the existing date.")
            else:
                transaction.date = form.trans_date.data
                db.session.commit()
                flash_note += [0]

        if form.trans_amount.data:
            if form.trans_amount.data == transaction.amount:
                flash("The new amount you've entered matches the existing amount.")
            else:
                transaction.change_trans_amount(form.trans_amount.data)
                flash_note += [1]

        if form.trans_type.data != 'S':
            if form.trans_type.data == transaction.ttype:
                flash("The new type you've entered matches the existing type.")
            else:
                transaction.flip_trans_type()
                flash_note += [2]

        if form.trans_category.data != 0:
            if form.trans_category.data == transaction.id_budget_category:
                flash("The new category you've entered matches the existing category.")
            else:
                transaction.change_trans_category(form.trans_category.data)
                flash_note += [3]

        if form.trans_vendor.data:
            if form.trans_vendor.data == transaction.vendor:
                flash("The new vendor you've entered matches the existing vendor.")
            else:
                transaction.vendor = form.trans_vendor.data
                db.session.commit()
                flash_note += [4]

        if form.trans_note.data:
            if form.trans_note.data == transaction.note:
                flash("The new note you've entered matches the existing note.")
            else:
                transaction.note = form.trans_note.data
                db.session.commit()
                flash_note += [5]

        db.session.commit()

        if 0 in flash_note:
            flash("The transaction date has been changed.")
        if 1 in flash_note:
            flash("The transaction amount has been changed.")
        if 2 in flash_note:
            flash("The transaction type has been changed.")
        if 3 in flash_note:
            flash("The transaction budget category has been changed.")
        if 4 in flash_note:
            flash("The transaction vendor has been changed.")
        if 5 in flash_note:
            flash("The transaction note has been changed.")

        return redirect(url_for('main.trans_edit'))


    return render_template('transactions/edit.html',
                        title='Edit Transactions',
                        form=form,
                        transactions=transactions
                        )


@bp.route('/trans/delete', methods=['GET','POST'])
@login_required
def trans_delete():
    page = request.args.get('page',1,type=int)

    trans_choices = [(c.id,c.amount) for c in current_user.transactions.order_by(Transaction.date.desc()).all()]
    transactions = current_user.transactions.order_by(Transaction.date.desc()).all()

    form = DeleteTransactionForm()

    form.select_trans.choices = trans_choices
    
    if form.validate_on_submit():

        transaction = current_user.transactions.filter_by(id=form.select_trans.data).first()
        transaction.unapply_transaction()

        db.session.delete(transaction)
        db.session.commit()

        flash("The transaction you've selected has been deleted.")
        return redirect(url_for("main.trans_delete"))

    return render_template('transactions/delete.html',
                    title='Delete Transactions',
                    form=form,
                    transactions=transactions
                    )

@bp.route('/trans/view"', methods=['GET','POST'])
@login_required
def trans_view():
    page = request.args.get('page',1,type=int)

    transactions = current_user.transactions.order_by(Transaction.date.desc()).paginate(page,
        10, False)
    next_url = url_for('main.trans_view', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('main.trans_view', page=transactions.prev_num) \
        if transactions.has_prev else None

    return render_template('transactions/view.html',
                            title='View Transactions',
                            transactions=transactions.items,
                            next_url=next_url,
                            prev_url=prev_url
                            )