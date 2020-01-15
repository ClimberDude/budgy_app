# TODO: update the import form to include transactions formatted 
#   as they are in the exported csv files

def import_trans_from_csv(trans_file):

    import csv
    from app import db
    from app.models import User, Budget_Category, Budget_History, Transaction
    from datetime import datetime
    from flask import flash
    # from flask_login import current_user
    from flask_security import current_user

    transaction_reader=csv.reader(trans_file,delimiter=",")
    count = 0
    for row in transaction_reader:
        if row[0] != 'Transactions' and row[0] != '':
            if row[5] != "Take Home Pay":
                amount = row[4].replace(',','')
                if float(amount) < 0:
                    if row[6][:8] == 'Transfer' or row[6][:8] == 'transfer':
                        ttype = 'TI'
                    else:
                        ttype = 'I'

                    amount=amount.replace('-','')
                else:
                    if row[6][:8] == 'Transfer' or row[6][:8] == 'transfer':
                        ttype = 'TE'
                    else:
                        ttype = 'E'

                transaction = Transaction(id_user=current_user.id,
                                            id_budget_category=current_user.budget_categories.filter_by(category_title=row[5]).first().id,
                                            date=datetime.strptime(row[3],"%m/%d/%Y"),
                                            amount=float(amount),
                                            note=row[6],
                                            ttype=ttype
                                            )

                db.session.add(transaction)
                db.session.commit()

                transaction.apply_transaction()
                count+=1

    flash("{} transactions have been added".format(count))

def import_budgets_from_csv(budget_file):

    import csv
    from app import db
    from app.models import User, Budget_Category, Budget_History, Transaction
    from datetime import datetime
    from flask import flash
    from flask_login import current_user

    budget_reader=csv.reader(budget_file,delimiter=",")
    count = [0,0,0]
    for row in budget_reader:

        if row[0] == 'Budgets':
            year=row[1]
            budget_date = row[1]+'-01-01'
        
        elif row[0] != 'Budgets' and row[0] != '':
            budget_category = current_user.budget_categories.filter_by(category_title=row[1]).first()
            if row[4] == '':
                row[4] = 0.0

            if budget_category:
                count[2] += 1
            else:
                budget_category = Budget_Category(id_user=current_user.id,
                                                category_title=row[1],
                                                spending_category=row[2],
                                                current_balance=round(float(row[4]),2),
                                                status='A'
                                                )

                db.session.add(budget_category)
                db.session.commit()

                budget_history = Budget_History(id_user=current_user.id,
                                                id_budget_category=budget_category.id,
                                                start_datetime=datetime.strptime(budget_date,"%Y-%m-%d"),
                                                status = 'C',
                                                annual_budget=round(float(row[3]),2)*12)

                db.session.add(budget_history)
                db.session.commit()
                count[0] += 1

            for i in range(12):
                if row[i+5]:
                    fund_date = year +"-{}-01".format(i+1)

                    transaction = Transaction(id_user = current_user.id,
                                id_budget_category = budget_category.id,
                                date=datetime.strptime(fund_date,"%Y-%m-%d"),
                                amount = row[i+5],
                                vendor = None,
                                note = "Allocated by batch funding.",
                                ttype = "I")
                    db.session.add(transaction)
                    db.session.commit()

                    transaction.apply_transaction()
                    count[1] += 1

    flash("{} budgets have been created, {} budgets already existed, with {} income transactions applied.".format(count[0],count[2],count[1]))

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
