from app import db, login
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    budget_categories = db.relationship('Budget_Category', cascade='delete, delete-orphan', backref='user', lazy='dynamic')
    budget_histories = db.relationship('Budget_History', cascade='delete, delete-orphan', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', cascade='delete, delete-orphan', backref='user', lazy='dynamic')
    unallocated_income = db.Column(db.DECIMAL)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Budget_Category(db.Model):
    __tablename__ = 'budget_category'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_title = db.Column(db.String(64), index=True, unique=True)
    spending_category = db.Column(db.String(64), index=True)
    current_balance = db.Column(db.DECIMAL)
    budget_history = db.relationship('Budget_History', cascade='delete, delete-orphan', backref='budget_category',lazy='dynamic')
    status = db.Column(db.CHAR,index=True,default="A")
    transactions = db.relationship('Transaction',backref='budget_category',lazy='dynamic')

    def __repr__(self):
        return '<Budget Category {}>'.format(self.category_title)

    def fund_budget(self,amount):
        self.current_balance += amount

class Budget_History(db.Model):
    __tablename__ = 'budget_history'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_budget_category = db.Column(db.Integer, db.ForeignKey('budget_category.id'))
    start_datetime = db.Column(db.DateTime, default=datetime.now())
    end_datetime = db.Column(db.DateTime, nullable=True, default=None)
    status = db.Column(db.CHAR, index=True)
    annual_budget = db.Column(db.DECIMAL)

    def __repr__(self):
        return '<Budget History {}>'.format(self.status)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_budget_category = db.Column(db.Integer, db.ForeignKey('budget_category.id'))
    date = db.Column(db.Date, index=True, default=datetime.now().date())
    amount = db.Column(db.DECIMAL, index=True)
    vendor = db.Column(db.String(140))
    note = db.Column(db.String(140))
    ttype = db.Column(db.CHAR,index=True)

    def __repr__(self):
        return '<Transaction on {} at {}: ${}>'.format(self.date, self.vendor, self.amount)

    def apply_transaction(self):
        if self.ttype == 'E':
            self.budget_category.current_balance -= self.amount
            db.session.commit()
        elif self.ttype == 'I':
            self.budget_category.current_balance += self.amount
            db.session.commit()

    def unapply_transaction(self):
        if self.ttype == 'E':
            self.budget_category.current_balance += self.amount
            db.session.commit()
        elif self.ttype == 'I':
            self.budget_category.current_balance -= self.amount
            db.session.commit()

    def change_trans_amount(self, amount):
        self.unapply_transaction()
        self.amount = amount
        db.session.commit()
        self.apply_transaction()

    def change_trans_type(self):
        self.unapply_transaction()
        if self.ttype == 'E':
            self.ttype = 'I'
        elif self.ttype == 'I':
            self.ttype = 'E'
        db.session.commit()
        self.apply_transaction()
    
    def change_trans_category(self, id_new_category):
        self.unapply_transaction()
        self.id_budget_category = id_new_category
        db.session.commit()
        self.apply_transaction()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))