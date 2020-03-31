from app import db
from app.models import User, Budget_Category, Budget_History, Transaction

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from flask import flash, jsonify
# from flask_login import current_user
from flask_security import current_user

import numpy as np

from sqlalchemy.sql import func

def income_v_spending_plot(**kwargs):
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    budget = kwargs.get('budget', 0)
    category = kwargs.get('category', 'all')

    #initial, "unfiltered" database query returning all transactions 
    #(filtered by user id to show only relevant transactions and by IDs to remove duplicates)
    #Budget Category and Transaction tables joined to allow filtering by columns in both tables. 
    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_user==current_user.id).filter(Transaction.id_budget_category==Budget_Category.id)

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

    label_date = [start_date]

    for i in range(diff_month):
        label_date.append(label_date[i] + relativedelta(months=+1))
        month_trans = transactions.filter(Transaction.date.between(label_date[i]-relativedelta(minutes=5),label_date[i+1]-relativedelta(days=+1)))
        
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

    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_user==current_user.id).filter(Transaction.id_budget_category==Budget_Category.id)

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

    data = {'label':'Spending by Category'}

    labels = np.array([])
    data_expenses = np.array([])

    if budget_or_spending == 0: #Separate by Budget Categories
        
        #loop through all active budget categories for the current user
        for budget_categ in current_user.budget_categories.filter_by(status="A").all():
            #for a given category, find all transactions posted for that category
            budget_trans = transactions.filter(Budget_Category.category_title == budget_categ.category_title)
            #sum all the transactions for the category that are of a given type, E for expense in this case
            budget_expense_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "E")
            #add the category title to the label list
            labels = np.append(labels,budget_categ.category_title)
            #add the sum to a list of sums for expenses, specifically
            data_expenses = np.append(data_expenses, float(budget_expense_sum.scalar() if budget_expense_sum.scalar() != None else 0))

    elif budget_or_spending == 1: #Separate by Spending Categories
        
        for spending_categ in  db.session.query(Budget_Category.spending_category).filter(Budget_Category.id_user==current_user.id).distinct().all():
            spending_trans = transactions.filter(Budget_Category.spending_category == spending_categ[0])
            spending_expense_sum = spending_trans.with_entities(func.sum(Transaction.amount).label("Spending Sum")).filter(Transaction.ttype == "E")
            labels = np.append(labels,spending_categ[0])
            data_expenses = np.append(data_expenses,float(spending_expense_sum.scalar() if spending_expense_sum.scalar() != None else 0))

    idx = np.argsort(data_expenses)

    labels = labels[idx]
    data_expenses = data_expenses[idx]

    data['labels'] = labels.tolist()
    data['data_expenses'] = data_expenses.tolist()

    return data

def summary_table(**kwargs):
    start_month = kwargs.get('start_month', datetime.today().month)
    start_year = kwargs.get('start_year', datetime.today().year)
    span = kwargs.get('span', 3)
    prior_or_following = kwargs.get('prior_or_following', 0)

    transactions = db.session.query(Budget_Category,Transaction).filter(Transaction.id_user==current_user.id).filter(Transaction.id_budget_category==Budget_Category.id)
    
    start_date = datetime.strptime("{}:{}".format(start_year,start_month),"%Y:%m")
    
    if prior_or_following == 0:
        start = start_date - relativedelta(months=+span-1)
        end = start_date + relativedelta(months=+1)
    else:
        start = start_date
        end = start_date + relativedelta(months=+span)

    start = start - relativedelta(minutes=1)
    end = end - relativedelta(days=+1)

    data = {'label':'Monthly Summary',
            'month':{},
            'data_expenses':[],
            'data_income':[]
            }

    label_date = [start_date]
    data['month']["Span Sum"] = []

    #Calculates a sum of all months in selected span for a particular budget
    for budget_categ in current_user.budget_categories.filter_by(status="A").all():

        budget_trans = transactions.filter(Transaction.date.between(start,end)).filter(Budget_Category.category_title == budget_categ.category_title)
        budget_expense_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "E")
        budget_income_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "I")

        data['month']["Span Sum"].append((budget_categ.category_title,
            float(budget_expense_sum.scalar() if budget_expense_sum.scalar() != None else 0),
            float(budget_income_sum.scalar() if budget_income_sum.scalar() != None else 0)))


    for i in range(span):
        if prior_or_following == 0:
            label_date.append(label_date[i] + relativedelta(months=-1))
            start = label_date[i]
            end = label_date[i] + relativedelta(months=+1)
        else:
            label_date.append(label_date[i] + relativedelta(months=+1))
            start = label_date[i]
            end = label_date[i+1]

        start = start - relativedelta(minutes=1)
        end = end - relativedelta(days=+1)

        data['month'][str(label_date[i])] = []
        month_trans = transactions.filter(Transaction.date.between(start,end))
        
        #calculates a sum of all budgets for a particular month
        month_expense_sum = month_trans.with_entities(func.sum(Transaction.amount).label("Month Sum")).filter(Transaction.ttype == "E")
        month_income_sum = month_trans.with_entities(func.sum(Transaction.amount).label("Month Sum")).filter(Transaction.ttype == "I")
        data['month'][str(label_date[i])].append(("Monthly Sum",
            float(month_expense_sum.scalar() if month_expense_sum.scalar() != None else 0),
            float(month_income_sum.scalar() if month_income_sum.scalar() != None else 0)))

        #Calculates a sum of a particulary budget for a particular month
        for budget_categ in current_user.budget_categories.filter_by(status="A").all():

            budget_trans = month_trans.filter(Budget_Category.category_title == budget_categ.category_title)
            budget_expense_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "E")
            budget_income_sum = budget_trans.with_entities(func.sum(Transaction.amount).label("Budget Sum")).filter(Transaction.ttype == "I")

            data['month'][str(label_date[i])].append((budget_categ.category_title,
                float(budget_expense_sum.scalar() if budget_expense_sum.scalar() != None else 0),
                float(budget_income_sum.scalar() if budget_income_sum.scalar() != None else 0)))

    #processes the data to a format that is more easily exported to HTML table
    table_builder = {'header1':['Category','Span Sum'],
                    'header2':[['Expense','Income']],
                    'Monthly Sum':[]
                    }

    for month in data['month'].keys():
        if month not in table_builder['header1']:
            table_builder['header1'].append(month[:7])
            table_builder['header2'].append(['Expense','Income'])

        for category in data['month'][month]:
            if category[0] not in table_builder.keys():
                table_builder[category[0]] = [(category[1],category[2])]
            else:
                table_builder[category[0]].append((category[1],category[2]))

    return table_builder