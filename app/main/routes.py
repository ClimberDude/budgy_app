from app import db, table_builder, scheduled_tasks
from app.main import bp, csv_rw
from app.main.forms import AddBudgetForm, AddBatchBudgetForm, EditBudgetForm, DeleteBudgetForm, \
                            AddTransactionForm, AddBatchTransactionForm, EditTransactionForm, EditRepTransactionForm, DeleteTransactionForm, \
                            TransferForm, FundingForm, DownloadTransactionForm, DownloadBudgetForm

from app.models import User, Budget_Category, Budget_History, Transaction, Scheduled_Transaction

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app
# from flask_login import current_user, login_required
from flask_security import current_user, login_required
from io import StringIO
import simplejson as json

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/landing', methods=['GET', 'POST'])
def landing():
    return render_template('landing.html',
                            title='Landing Page')

###########################################################################################################################
# Route functions related to handling the budget categories
###########################################################################################################################

@bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def budget_add():
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()

    form=AddBudgetForm()
    form_batch=AddBatchBudgetForm()

    if form.validate_on_submit():

        budget_category= Budget_Category(id_user = current_user.id,
                                         category_title = form.category_title.data.title(),
                                         spending_category = form.spending_category.data.title(),
                                         current_balance = form.current_balance.data,
                                         status='A')

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
                                        start_datetime = datetime.now(),
                                        status = 'C',
                                        annual_budget = annual_budget)

        db.session.add(budget_history)
        db.session.commit()

        flash('Category {} has been added.'.format(budget_category.category_title))
        return redirect(url_for('main.budget_add'))

    if form_batch.validate_on_submit():
        try:
            if form_batch.budget_csv_file.data:
                file = form_batch.budget_csv_file.data.read().decode('utf-8')
                csv_rw.import_budgets_from_csv(StringIO(file))
                return redirect(url_for('main.budget_add'))
        except:
            flash('There was an error processing your csv file.')    


    return render_template('budgets/add.html',
                           title='Add Budget',
                           form=form,
                           form_batch=form_batch,
                           budget_categories=budget_categories)

@bp.route('/budget/edit', methods=['GET', 'POST'])
@login_required
def budget_edit():
    #Populate the list of radio button choices with the current list of
    #budget categories
    radio_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]

    #Pull all the current data for the categories for the current user, to display
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()

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
                category.category_title = form.category_title.data.title()
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
                obsolete_history.end_datetime = datetime.now()
                obsolete_history.status = 'O'

                #Next, create the new budget history entry from the entered form data
                current_history = Budget_History(id_user = current_user.id,
                                                 id_budget_category = category.id,
                                                 start_datetime = datetime.now(),
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
                            title='Edit Budget',
                           form=form,
                           budget_categories=budget_categories)

@bp.route('/budget/delete', methods=['GET','POST'])
@login_required
def budget_delete():
    #Populate the list of radio button choices with the current list of
    #budget categories
    radio_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]

    #Pull all the current data for the categories for the current user, to display
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()

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
            if category.transactions.first() != None:
                flash("The category you are trying to delete has transactions posted against it and cannot be deleted.")
                return redirect(url_for('main.budget_delete'))
            else:
                db.session.delete(category)
                db.session.commit()

                flash('The budget category has been deleted.')
                return redirect(url_for('main.budget_delete'))

        elif delete_or_end == 2:
            category.status = 'E'
            db.session.commit()

            flash("The budget category has been ended, but historical data has been retained.")
            return redirect(url_for('main.budget_delete'))

    return render_template('budgets/delete.html',
                            title='Delete/End Budget',
                            form=form,
                            budget_categories=budget_categories)

@bp.route('/budget/view', methods=['GET','POST'])
@login_required
def budget_view():
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title.asc()).all()
        
    form=DownloadBudgetForm()

    if form.validate_on_submit():
        return redirect(url_for('main.download_budgets'))

    return render_template('budgets/view.html',
                            title='View Budgets',
                            budget_categories=budget_categories,
                            form=form
                            )

@bp.route('/budget/fund', methods=['GET','POST'])
@login_required
def budget_fund():
    form_categories = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title.asc())]
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title.asc()).all()
    unallocated_income = current_user.unallocated_income

    form = FundingForm(fund_budgets=form_categories)

    i=0
    for budget in form.fund_budgets:
        budget.name = form_categories[i][0]
        budget.label = form_categories[i][1]
        budget.data['fund_value'] = 1
        i += 1

    if form.validate_on_submit():
        fund_sum = 0
        for budget in form.fund_budgets:
            if budget.data['fund_value'] != None:
                transaction = Transaction(id_user = current_user.id,
                            id_budget_category = budget.name,
                            amount = budget.data['fund_value'],
                            vendor = None,
                            note = "Allocated by funding.",
                            ttype = "I")
                fund_sum += budget.data['fund_value']
                db.session.add(transaction)
                db.session.commit()

                transaction.apply_transaction()
                flash("{} was allocated ${:.2f}".format(transaction.budget_category.category_title,transaction.amount))
        
        if form.unallocated_income.data:
            unallocated_income = unallocated_income + form.unallocated_income.data - fund_sum
        else:
            unallocated_income -= fund_sum

        current_user.unallocated_income = unallocated_income
        db.session.commit()

        flash("${:.2f} was unallocated, and was saved for future allocation.".format(unallocated_income))

        return redirect(url_for('main.budget_fund'))

    return render_template('budgets/fund.html',
                            title='Fund Budgets',
                            form=form,
                            budget_categories=budget_categories,
                            unallocated_income=unallocated_income
                            )

###########################################################################################################################
# Route functions related to handling transactions
###########################################################################################################################

@bp.route('/trans/add', methods=['GET','POST'])
@login_required
def trans_add():
    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()

    form = AddTransactionForm()
    form.trans_category.choices += budget_choices

    form_batch = AddBatchTransactionForm()

    if form_batch.validate_on_submit():
        try:
            if form_batch.trans_csv_file.data:
                file = form_batch.trans_csv_file.data.read().decode('utf-8')
                csv_rw.import_trans_from_csv(StringIO(file))
                return redirect(url_for('main.trans_add'))

        except:
            flash('There was an error processing your csv file.')    
        
        return redirect(url_for('main.trans_add'))

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

        if form.trans_sched.data:
            sched_trans_template = 
            st = scheduled_tasks.add_repeating_trans(transaction)
            if form.trans_sched_apply.data:
                transaction.apply_transaction()
                flash("Your transaction has been applied, and will repeat day {} of each month.".format(st.dotm))
            if not form.trans_sched_apply.data:
                flash("Your transaction has NOT been applied, but will be applied on day {} of each month going forward.".format(st.dotm))
        else:
            transaction.apply_transaction()
            flash("Your transaction has been applied.")        
        
        return redirect(url_for('main.trans_add'))

    return render_template('transactions/add.html',
                            title='Add Transactions',
                            form=form,
                            form_batch=form_batch,
                            budget_categories=budget_categories,
                            )

@bp.route('/trans/edit', methods=['GET','POST'])
@login_required
def trans_edit():
    trans_choices = [(c.id,c.amount) for c in current_user.transactions.order_by(Transaction.date.desc()).all()]
    transactions = current_user.transactions.order_by(Transaction.date.desc()).all()
    
    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]

    form = EditTransactionForm() 
    form.select_trans.choices = trans_choices
    form.trans_category.choices += budget_choices

    if form.validate_on_submit():
        transaction = current_user.transactions.filter_by(id=form.select_trans.data).first()
        flash_note = []

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
                transaction.change_trans_type()
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
                        transactions=transactions,
                        )

@bp.route('/trans/edit_rep', methods=['GET','POST'])
@login_required
def trans_edit_rep():
    trans_choices = [(c.id,c.dotm) for c in current_user.scheduled_transactions.order_by(Scheduled_Transaction.dotm.asc()).all()]
    transactions = current_user.scheduled_transactions.order_by(Scheduled_Transaction.dotm.asc()).all()
    
    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]

    form=EditRepTransactionForm()
    form.select_trans.choices = trans_choices
    form.trans_category.choices += budget_choices

    
    return render_template('transactions/edit_rep.html',
                    title='Edit Repeating Transactions',
                    form=form,
                    transactions=transactions,
                    )


@bp.route('/trans/delete', methods=['GET','POST'])
@login_required
def trans_delete():
    # TODO: ended budget categories still have transactions visible. Is this a bug or a feature? The whole point of 
    #   allowing budgets to be ended rather than deleted was to retain the historical data on spending. 
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
                    transactions=transactions,
                    )

@bp.route('/trans/view', methods=['GET','POST'])
@login_required
def trans_view():
    transactions = current_user.transactions.order_by(Transaction.date.desc()).all()
    form = DownloadTransactionForm()

    if form.validate_on_submit():
        return redirect(url_for('main.download_trans'))

    return render_template('transactions/view.html',
                            title='View Transactions',
                            transactions=transactions,
                            form=form
                            )

@bp.route('/trans/transfer',methods=['GET','POST'])
@login_required
def trans_transfer():
    budget_categories = current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()

    budget_choices = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title).all()]

    form = TransferForm()

    form.from_category.choices += budget_choices
    form.to_category.choices += budget_choices

    if form.validate_on_submit():
        if form.from_category.data == 'S':
            flash('Please enter a budget to transfer from.')
        elif form.to_category.data == 'S':
            flash('Please enter a budget to transfer to.')
        else:
            from_category = current_user.budget_categories.filter_by(id=form.from_category.data).first()
            to_category = current_user.budget_categories.filter_by(id=form.to_category.data).first()

            from_transaction = Transaction(id_user = current_user.id,
                                    id_budget_category = form.from_category.data,
                                    amount = form.trans_amount.data,
                                    note = "Transfer to {}".format(to_category.category_title),
                                    ttype = "TE")
            db.session.add(from_transaction)

            to_transaction = Transaction(id_user = current_user.id,
                                    id_budget_category = form.to_category.data,
                                    amount = form.trans_amount.data,
                                    note = "Transfer from {}".format(from_category.category_title),
                                    ttype = "TI")
            db.session.add(to_transaction)
            db.session.commit()
            
            from_transaction.apply_transaction()
            to_transaction.apply_transaction()
            
            flash("${:.2f} was transfered from {} to {}".format(form.trans_amount.data, 
                                                                from_category.category_title,
                                                                to_category.category_title))

        return redirect(url_for('main.trans_transfer'))

    return render_template('transactions/transfer.html',
                        title='Transfer',
                        form=form,
                        budget_categories=budget_categories
                        )

###########################################################################################################################
# Route functions related to AJAX & file download calls
###########################################################################################################################

@bp.route('/retr_trans_view', methods=['GET','POST'])
@login_required
def retr_trans_view():
    data = table_builder.collect_data_serverside_trans_view(request, current_user)
    return json.dumps(data)

@bp.route('/retr_trans_select', methods=['GET','POST'])
@login_required
def retr_trans_select():
    data = table_builder.collect_data_serverside_trans_select(request, current_user)
    return json.dumps(data)

@bp.route('/retr_budget_view', methods=['GET','POST'])
@login_required
def retr_budget_view():
    data = table_builder.collect_data_serverside_budget_view(request, current_user)
    return json.dumps(data)

@bp.route('/retr_budget_select', methods=['GET','POST'])
@login_required
def retr_budget_select():
    data = table_builder.collect_data_serverside_budget_select(request, current_user)
    return json.dumps(data)

@bp.route('/download_trans',methods=['GET','POST'])
@login_required
def download_trans():
    try:
        output = csv_rw.export_trans_to_csv()
        return output
    except:
        flash('There was an error downloading your transactions','error')
        return redirect(url_for('main.trans_view'))

@bp.route('/download_budgets',methods=['GET','POST'])
@login_required
def download_budgets():
    try:
        output = csv_rw.export_budget_to_csv()
        return output
    except:
        flash('There was an error downloading your transactions','error')
        return redirect(url_for('main.budget_view'))