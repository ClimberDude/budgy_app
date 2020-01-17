from app import create_app, db
from app.models import User, Transaction, Scheduled_Transaction

from datetime import date
from flask_security import current_user

app = create_app()

def add_repeating_trans(transaction):
    st = Scheduled_Transaction(id_user=current_user.id,
                                id_transaction=transaction.id,
                                dotm = transaction.date.day )
    db.session.add(st)
    db.session.commit()

    return st

def apply_repeating_trans():
    with app.app_context():
        today = int(date.today().day)
        users = User.query.all()
        
        for user in users:

            st = user.scheduled_transactions.filter_by(dotm=today).filter_by(id_user=user.id).all()
            
            for trans in st:
                transaction = Transaction.query.filter_by(id=trans.id_transaction).first()
                transaction.date = date.today()
                transaction.note = 'Repeating transaction - applied automatically'

                db.session.add(transaction)
                db.session.commit()

                transaction.apply_transaction()