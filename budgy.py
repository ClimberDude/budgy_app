from app import create_app, db, login

from app.models import User, Role, Budget_Category, Budget_History, \
                        Transaction, Scheduled_Transaction
from flask import redirect, url_for

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db':db,
            'User':User,
            'Role':Role,
            'Budget_Category':Budget_Category,
            'Budget_History':Budget_History,
            'Transaction':Transaction,
            'Scheduled_Transaction':Scheduled_Transaction,
            }

@app.login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))

@app.before_first_request
def before_first_request():
    db.create_all()
    
    if not Role.query.filter(Role.name=='User').first():

        role_user = Role(name='User', description='Standard user access privileges')
        db.session.add(role_user)

    if not Role.query.filter(Role.name=='Admin').first():

        role_admin = Role(name='Admin', description='Standard user access privileges + Admin access')
        db.session.add(role_admin)

    db.session.commit()