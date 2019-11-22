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
    budget_categories = db.relationship('Budget_Category', backref='user', lazy='dynamic')
    budget_histories = db.relationship('Budget_History', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

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
    category_title = db.Column(db.String(64), index=True)
    current_balance = db.Column(db.DECIMAL)
    budget_history = db.relationship('Budget_History',backref='budget_category',lazy='dynamic')
    # TODO: add an active or ended column to the database to keep track of categories that have 
    #   been ended by the user.

    def __repr__(self):
        return '<Budget Category {}>'.format(self.category_title)


class Budget_History(db.Model):
    __tablename__ = 'budget_history'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_budget_category = db.Column(db.Integer, db.ForeignKey('budget_category.id'))
    start_datetime = db.Column(db.DateTime, default=datetime.utcnow())
    end_datetime = db.Column(db.DateTime, nullable=True, default=None)
    status = db.Column(db.CHAR, index=True)
    annual_budget = db.Column(db.DECIMAL)

    def __repr__(self):
        return '<Budget History {}>'.format(self.status)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.String, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_budget_category = db.Column(db.Integer, db.ForeignKey('budget_category.id'))
    date = db.Column(db.Date, index=True, default=datetime.utcnow().date())
    amount = db.Column(db.DECIMAL)
    vendor = db.Column(db.String(140))
    note = db.Column(db.String(140))

    def __repr__(self):
        return '<Transaction at {}: ${}>'.format(self.vendor, self.amount)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))