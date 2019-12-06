from app import db
from app.models import User, Budget_Category, Budget_History, Transaction

from datetime import datetime

from flask import flash, jsonify
from flask_login import current_user

def income_v_spending_plot(**kwargs):
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    budget = kwargs.get('budget', 0)
    category = kwargs.get('category', 'all')

    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_budget_category==Budget_Category.id)

    if not start_date:
        start_date = current_user.transactions.order_by(Transaction.date.asc()).first().date
    transactions = transactions.filter(Transaction.date >= start_date)
        
    if not end_date:
        end_date = datetime.now().date()
    transactions = transactions.filter(Transaction.date <= end_date)

    if budget:
        transactions = transactions.filter(Transaction.id_budget_category==budget)

    if category != 'all':
        transactions = transactions.filter(Budget_Category.spending_category==category)

    data = {'label':'Monthly Income vs Spending',
            'labels':[],
            'data_expenses':[],
            'data_income':[]
            }

    data_expenses = {}
    data_income = {}

    for item in transactions.all():
        if [item[1].date.strftime('%Y-%b')] not in data['labels']:
            data['labels'].append([item[1].date.strftime('%Y-%b')])

        if item[1].ttype == 'I':
            if item[1].date.strftime('%Y-%b') not in data_income:
                data_income[item[1].date.strftime('%Y-%b')] = round(float(item[1].amount),2)
            else:
                data_income[item[1].date.strftime('%Y-%b')] += round(float(item[1].amount),2)
        elif item[1].ttype == 'E':
            if item[1].date.strftime('%Y-%b') not in data_expenses:
                data_expenses[item[1].date.strftime('%Y-%b')] = round(float(item[1].amount),2)
            else:
                data_expenses[item[1].date.strftime('%Y-%b')] += round(float(item[1].amount),2)

    data['labels']

    for item in data['labels']:
        if item[0] in data_expenses.keys():
            data['data_expenses'].append(round(data_expenses[item[0]],2))
        if item[0] in data_income.keys():
            data['data_income'].append(round(data_income[item[0]],2))            

    return data

def spending_by_category_plot(**kwargs):
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    budget_or_spending = kwargs.get('budget_or_spending', 0)

    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_budget_category==Budget_Category.id)

    if not start_date:
        start_date = current_user.transactions.order_by(Transaction.date.asc()).first().date
    transactions = transactions.filter(Transaction.date >= start_date)
        
    if not end_date:
        end_date = datetime.now().date()
    transactions = transactions.filter(Transaction.date <= end_date)

    data = {'label':'Spending by Category',
        'labels':[],
        'data_expenses':[],
        'data_income':[]
        }

    data_expenses = {}
    data_income = {}

    if budget_or_spending == 0: #Separate by Budget Categories
        for item in transactions.all():
            if item[1].ttype == 'E':
                if [item[0].category_title] not in data['labels']:
                    data['labels'].append([item[0].category_title])
                if item[0].category_title not in data_expenses:
                    data_expenses[item[0].category_title] = round(float(item[1].amount),2)
                else:
                    data_expenses[item[0].category_title] += round(float(item[1].amount),2)
    
    elif budget_or_spending == 1: #Separate by Budget Categories
        for item in transactions.all():
            if item[1].ttype == 'E':
                if [item[0].spending_category] not in data['labels']:
                    data['labels'].append([item[0].spending_category])
                if item[0].spending_category not in data_expenses:
                    data_expenses[item[0].spending_category] = round(float(item[1].amount),2)
                else:
                    data_expenses[item[0].spending_category] += round(float(item[1].amount),2)

    data['labels'].sort()

    for item in data['labels']:
        data['data_expenses'].append(round(data_expenses[item[0]],2))

    return data