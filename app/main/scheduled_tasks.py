from app import create_app, db
from app.models import User, Transaction, Scheduled_Transaction

from datetime import date
from flask_security import current_user

app = create_app()

def add_scheduled_trans(transaction):
    st = Scheduled_Transaction(id_user=current_user.id,
                                id_transaction=transaction.id,
                                dotm = transaction.date.day )
    db.session.add(st)
    db.session.commit()

    return st

def apply_scheduled_trans():
    with app.app_context():
        today = int(date.today().day)
        users = User.query.all()
        
        for user in users:

            st = user.scheduled_transactions.filter_by(dotm=today).filter_by(id_user=user.id).all()
            
            for trans in st:
                #pull up the transaction template to populate the new transaction
                trans_template = Transaction.query.filter_by(id=trans.id_transaction).first()

                #apply template values (where appropriate) to the new transaction
                transaction = Transaction(id_user = trans_template.id_user,
                                            id_budget_category = trans_template.id_budget_category,
                                            date = date.today(),
                                            amount = trans_template.amount,
                                            vendor = trans_template.vendor,
                                            note = 'Repeating transaction - applied automatically',
                                            ttype = trans_template.ttype[-1])

                db.session.add(transaction)
                db.session.commit()

                transaction.apply_transaction()