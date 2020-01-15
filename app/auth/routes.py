from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, DownloadForm
from app.auth.email import send_password_reset_email
from app.models import User, Role, Transaction
from flask import render_template, redirect, url_for, flash, request
# from flask_login import login_user, logout_user, current_user
from flask_security import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET','POST'])
def login():
    #Checks if user is already authenticated by flask-login
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))

    form=LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        #Checks if user exists in database, or if supplied password hashes match
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        #uses flask-login to log user in
        login_user(user, remember=form.remember_me.data)

        #redirects user to the page they were trying to access, defaults to 'main.landing'
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.landing')
        return redirect(next_page)

    return render_template('login.html',
                           title='Login',
                           form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.landing'))

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))

    form=RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    unallocated_income=0.0,)
                    # roles=)

        #sets password using method in user model
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Congratulations! You've successfully registered with Budgy!")

        return redirect(url_for('auth.login'))

    return render_template('register.html',
                           title='Register',
                           form=form)

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    #assumes that a currently authenticated user won't need password reset.
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))

    form=ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash("We've just sent you an email with instructions on how to reset your password. Please check your inbox.")
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password',
                           form=form)

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.landing'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfully reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html',
                           title='Reset Password',
                           form=form)

@login_required
@bp.route('/profile', methods=['GET','POST'])
def profile():
    transactions = current_user.transactions
    date = transactions.order_by(Transaction.date.asc()).first().date

    form = DownloadForm()

    if form.validate_on_submit():
        if form.select_data.data == 1:
            return redirect(url_for('main.download_budgets'))

        if form.select_data.data == 2:
            return redirect(url_for('main.download_trans'))

    return render_template('profile.html',
                            title='Profile',
                            user=current_user,
                            date=date,
                            form=form
                            )