# TODO: update the import form to include transactions formatted 
#   as they are in the exported csv files

import csv
from app import db
from app.models import User, Budget_Category, Budget_History, Transaction
from datetime import datetime
from decimal import Decimal
from flask import flash
# from flask_login import current_user
from flask_security import current_user

two_places = Decimal(10) ** -2

def import_trans_from_csv(trans_file):

    budget_categories = current_user.budget_categories
    transaction_reader=csv.reader(trans_file,delimiter=",")
    count = 0
    for row in transaction_reader:
        if row[0] != 'Transactions' and row[0] != '':
            user_id = current_user.id
            budget_id = budget_categories.filter_by(category_title=row[4]).first().id
            date = datetime.strptime(row[1],"%Y-%m-%d")
            amount = Decimal(row[2]).quantize(two_places)
            vendor = row[5]
            note = row[6]
            ttype = row[3]

            transaction = Transaction(id_user=user_id,
                            id_budget_category=budget_id,
                            date=date,
                            amount=amount,
                            note=note,
                            ttype=ttype
                            )

            db.session.add(transaction)
            db.session.commit()

            count+=1

    flash("{} transactions have been added".format(count))

def import_budgets_from_csv(budget_file):

    budget_categories = current_user.budget_categories
    budget_reader=csv.reader(budget_file,delimiter=",")
    count = 0
    for row in budget_reader:
        if row[0] != 'Budgets' and row[0] != '':

            user_id = current_user.id
            category_title = str(row[1])
            spending_category = row[2]
            current_balance = Decimal(row[3]).quantize(two_places)
            status_cat = row[4]

            if not budget_categories.filter_by(category_title=category_title).first():

                budget_category = Budget_Category(id_user=user_id,
                                    category_title=category_title,
                                    spending_category=spending_category,
                                    current_balance=current_balance,
                                    status=status_cat
                                    )

                db.session.add(budget_category)
                db.session.commit()
                count+=1

                if status_cat == 'A':
                    hist_final_startdate = row[-2]
                elif status_cat == 'C':
                    hist_final_startdate = row[-3]
                hist_place = 6

                while row[hist_place] != hist_final_startdate:
                    start_datetime = datetime.strptime(row[hist_place].split('.')[0],"%Y-%m-%d %H:%M:%S")
                    end_datetime = datetime.strptime(row[hist_place+1].split('.')[0],"%Y-%m-%d %H:%M:%S")
                    annual_budget = Decimal(row[hist_place-1]).quantize(two_places)
                    status_hist = 'O'

                    budget_history = Budget_History(id_user=current_user.id,
                                    id_budget_category=budget_category.id,
                                    start_datetime=start_datetime,
                                    end_datetime=end_datetime,
                                    status = status_hist,
                                    annual_budget=annual_budget)

                    db.session.add(budget_history)
                    db.session.commit()

                    hist_place+=3

                start_datetime = datetime.strptime(row[hist_place].split('.')[0],"%Y-%m-%d %H:%M:%S")
                annual_budget = Decimal(row[hist_place-1]).quantize(two_places)
                status_hist = 'C'

                budget_history = Budget_History(id_user=current_user.id,
                                id_budget_category=budget_category.id,
                                start_datetime=start_datetime,
                                status = status_hist,
                                annual_budget=annual_budget)

                db.session.add(budget_history)
                db.session.commit()

    flash("{} budgets have been created.".format(count))

# Exporting transactions to the user as a properly formatted CSV file. 

def export_trans_to_csv():

    import csv
    import io
    from app import db
    from app.models import User, Budget_Category, Budget_History, Transaction
    from datetime import datetime
    from flask import flash, make_response
    # from flask_login import current_user
    from flask_security import current_user

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Transactions'])
    cw.writerow(['','Date','Amount','Type','Category','Vendor','Note'])

    trans_list = current_user.transactions.all()
    budget_list = current_user.budget_categories
    line=1
    for transaction in trans_list:
        date = str(transaction.date)
        amount = str(transaction.amount)
        ttype = str(transaction.ttype)
        category = str(budget_list.filter_by(id=transaction.id_budget_category).first().category_title)
        vendor = str(transaction.vendor) if transaction.vendor else ''
        note = str(transaction.note) if transaction.note else ''

        cw.writerow([str(line),date,amount,ttype,category,vendor,note])
        line+=1

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}_trans_export.csv".format(current_user.username)
    output.headers["Content-type"] = "text/csv"

    return output
                
def export_budget_to_csv():

    import csv
    import io
    from app import db
    from app.models import User, Budget_Category, Budget_History, Transaction
    from datetime import datetime
    from flask import flash, make_response
    # from flask_login import current_user
    from flask_security import current_user

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Budgets'])
    cw.writerow(['','Category Title','Spending Category','Current Balance','Status','Annual Budget','Start Date','End Date','...'])

    budget_list = current_user.budget_categories.all()
    history_list = current_user.budget_histories

    line=1
    for budget in budget_list:
        histories = history_list.filter_by(id_budget_category=budget.id)

        title = str(budget.category_title)
        sp_cat = str(budget.spending_category)
        cur_bal = str(budget.current_balance)
        status = str(budget.status)

        budget_write_list = [str(line),title,sp_cat,cur_bal,status]
        
        for hist in histories:
            annual = str(hist.annual_budget) if hist.annual_budget else '0.00'
            budget_write_list.append(annual)
            
            st_date = str(hist.start_datetime) if hist.start_datetime else ''
            budget_write_list.append(st_date)
            
            end_date = str(hist.end_datetime) if hist.end_datetime else ''
            budget_write_list.append(end_date)

        cw.writerow(budget_write_list)
        line+=1

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}_budget_export.csv".format(current_user.username)
    output.headers["Content-type"] = "text/csv"

    return output
