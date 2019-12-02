# TODO: update the import form to include transactions formatted 
#   as they are in the app itself

def import_trans_from_csv(trans_file):

    import csv
    from app import db
    from app.models import User, Budget_Category, Budget_History, Transaction
    from datetime import datetime
    from flask import flash
    from flask_login import current_user

    transaction_reader=csv.reader(trans_file,delimiter=",")
    count = 0
    for row in transaction_reader:

        if row[0] != 'Transactions' and row[0] != '':
            if row[5] != "Take Home Pay":
                if float(row[4].replace(',','')) < 0:
                    ttype = 'I'
                    row[4]=row[4].replace('-','')
                else:
                    ttype = 'E'

                transaction = Transaction(id_user=current_user.id,
                                            id_budget_category=current_user.budget_categories.filter_by(category_title=row[5]).first().id,
                                            date=datetime.strptime(row[3],"%m/%d/%Y"),
                                            amount=float(row[4].replace(',','')),
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
    count = [0,0]
    for row in budget_reader:

        if row[0] == 'Budgets':
            year=row[1]
            budget_date = row[1]+'-01-01'
        
        elif row[0] != 'Budgets' and row[0] != '':
            budget_category = current_user.budget_categories.filter_by(category_title=row[1]).first()
            if row[4] == '':
                row[4] = 0.0

            if budget_category:
                flash('The category {} already exists'.format(row[1]))
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

    flash("{} budgets have been created, with {} income transactions applied.".format(count[0],count[1]))


                    
