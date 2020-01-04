from app import db, admin
from app.models import User, Role, Budget_Category,Budget_History,Transaction   
from flask import url_for 
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_security import current_user
import os.path as op
        
class AdminView(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')

class FileAdminView(FileAdmin):
    def is_accessible(self):
        return current_user.has_role('Admin')

#TODO: figure out how to get url_for to work to add this link to the admin dashboard.
admin.add_link(MenuLink(name='Public Website', category='', url='/landing'))

admin.add_view(AdminView(User,db.session))
admin.add_view(AdminView(Role,db.session))
admin.add_view(AdminView(Budget_Category,db.session))
admin.add_view(AdminView(Budget_History,db.session))
admin.add_view(AdminView(Transaction,db.session))

path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdminView(path, '/static/', name='Static Files'))
