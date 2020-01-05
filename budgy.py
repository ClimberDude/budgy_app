from app import create_app, db
from app.models import User, Role

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db':db,
            'User':User}

@app.before_first_request
def before_first_request():
    db.create_all()
    
    if not Role.query.filter(Role.name=='User').first():

        role_user = Role(name='User', description='Standard user access priviliges')
        db.session.add(role_user)

    if not Role.query.filter(Role.name=='Admin').first():

        role_admin = Role(name='Admin', description='Standard user access priviliges + Admin access')
        db.session.add(role_admin)

    db.session.commit()