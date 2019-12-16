from app import db
from app.visuals import bp
from app.visuals import data_analysis as da
from app.visuals.forms import IncomeVSpendingVisForm, SpendingByCategoryVisForm

from app.models import User, Budget_Category, Budget_History, Transaction

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
# from flask_login import current_user, login_required
from flask_security import current_user, login_required
from io import StringIO

# @bp.route('/data_analysis', methods=['GET','POST'])
# @login_required
# def data_analysis():
#     data = da.spending_plot()
#     return jsonify(data)

@bp.route('/income_v_spending', methods=['GET', 'POST'])
@login_required
def income_v_spending():

    try:
        data = da.income_v_spending_plot()
    except:
        flash('There are currently no transaction. Add some to see visualizations!')
        return redirect(url_for('main.landing'))

    budget_categories = [(c.id,c.category_title) for c in current_user.budget_categories.filter_by(status='A').order_by(Budget_Category.category_title.asc()).all()]
    spending_categories = [(c.spending_category,c.spending_category) for c in Budget_Category.query.with_entities(Budget_Category.spending_category).distinct()]

    form = IncomeVSpendingVisForm()

    form.budget.choices += budget_categories
    form.category.choices += spending_categories

    if form.validate_on_submit():
        try:
            data = da.income_v_spending_plot(start_date=form.start_date.data,
                                end_date=form.end_date.data,
                                budget=form.budget.data,
                                category=form.category.data
                                )
        except:
            flash('There are currently no transaction. Add some to see visualizations!')
            return redirect(url_for('main.landing'))

        return render_template('income_v_spending.html',
                            title='Income vs Spending',
                            form=form,
                            data=data)

    return render_template('income_v_spending.html',
                            title='Income vs Spending',
                            form=form,
                            data=data)

@bp.route('/spending_by_category', methods=['GET', 'POST'])
@login_required
def spending_by_category():
    try:
        data = da.spending_by_category_plot()
    except:
        flash('There are currently no transaction. Add some to see visualizations!')
        return redirect(url_for('main.landing'))

    form = SpendingByCategoryVisForm()

    if form.validate_on_submit():
        try:
            data = da.spending_by_category_plot(start_date=form.start_date.data,
                                end_date=form.end_date.data,
                                budget_or_spending=form.budget_or_spending.data
                                )
        except:
            flash('There are currently no transaction. Add some to see visualizations!')
            return redirect(url_for('main.landing'))

        return render_template('spending_by_category.html',
                            title='Income vs Spending',
                            form=form,
                            data=data)

    return render_template('spending_by_category.html',
                            title='Income vs Spending',
                            form=form,
                            data=data)