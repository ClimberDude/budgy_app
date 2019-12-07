from app import db
from app.models import User, Budget_Category, Budget_History, Transaction

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import flash, jsonify
from flask_login import current_user

from sqlalchemy.sql import func

def income_v_spending_plot(**kwargs):
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    budget = kwargs.get('budget', 0)
    category = kwargs.get('category', 'all')

    #initial, "unfiltered" database query returning all transactions (filtered by IDs to remove duplicates)
    #Budget Category and Transaction tables joined to allow filtering by columns in both tables. 
    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_budget_category==Budget_Category.id)

    #set the default dates if no dates are provided in the form, then filter queries by dates.
    if not start_date:
        start_date = current_user.transactions.order_by(Transaction.date.asc()).first().date
    transactions = transactions.filter(Transaction.date >= start_date)
        
    if not end_date:
        end_date = datetime.now().date()
    transactions = transactions.filter(Transaction.date <= end_date)

    #calculate the span of time, in months, between the start and end date. 
    span = relativedelta(end_date,start_date)
    if span.days != 0:
        span.months += 1

    diff_month = span.years*12+span.months

    #filter by budget category if one is provided in the form. 
    if budget:
        transactions = transactions.filter(Transaction.id_budget_category==budget)

    #filter by spending category if one is provided in the form.
    if category != 'all':
        transactions = transactions.filter(Budget_Category.spending_category==category)

    data = {'label':'Monthly Income vs Spending',
            'labels':[],
            'data_expenses':[],
            'data_income':[]
            }

    label_date = []

    for i in range(diff_month):
        timedelta = relativedelta(months=+i)
        label_date.append(start_date + timedelta)
        month_trans = transactions.filter(Transaction.date.between(label_date[i],label_date[i]+relativedelta(months=+1)-relativedelta(days=+1)))
        
        month_income_sum = month_trans.with_entities(func.sum(Transaction.amount).label('Month Sum')).filter(Transaction.ttype == "I")
        month_expense_sum = month_trans.with_entities(func.sum(Transaction.amount).label('Month Sum')).filter(Transaction.ttype == "E")

        data['labels'].append(label_date[i].strftime('%Y-%m'))
        data['data_income'].append(float(month_income_sum.scalar() if month_income_sum.scalar() != None else 0))
        data['data_expenses'].append(float(month_expense_sum.scalar() if month_expense_sum.scalar() != None else 0))

    net = sum(data['data_income'])-sum(data['data_expenses'])
    
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

    if budget_or_spending == 0: #Separate by Budget Categories
        
        for budget_categ in current_user.budget_categories.filter_by(status="A").all():
            budget_trans = transactions.filter(Budget_Category.category_title == budget_categ.category_title)
            budget_expense_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "E")
            data['labels'].append(budget_categ.category_title)
            data['data_expenses'].append(float(budget_expense_sum.scalar() if budget_expense_sum.scalar() != None else 0))

    elif budget_or_spending == 1: #Separate by Spending Categories
        
        for spending_categ in  db.session.query(Budget_Category.spending_category).filter(Budget_Category.id_user==current_user.id).distinct().all():
            spending_trans = transactions.filter(Budget_Category.spending_category == spending_categ[0])
            spending_expense_sum = spending_trans.with_entities(func.sum(Transaction.amount).label("Spending Sum")).filter(Transaction.ttype == "E")
            data['labels'].append(spending_categ[0])
            data['data_expenses'].append(float(spending_expense_sum.scalar() if spending_expense_sum.scalar() != None else 0))

    return data