from app.mod_tables.models import TableBuilder

#TODO: figure out how to get apscheduler or flask-apscheduler working!
# from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config import Config
from dotenv import load_dotenv
from flask import Flask, request, current_app

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment

from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user,login_required, RoleMixin, Security, \
                            SQLAlchemyUserDatastore, UserMixin, utils

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

db = SQLAlchemy()
admin = Admin(name="Budgy")
bootstrap = Bootstrap()
mail = Mail()
migrate = Migrate(compare_type=True)
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
scheduler = APScheduler()
security = Security()
table_builder = TableBuilder()

# basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    admin.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    moment.init_app(app)
    login.init_app(app)

    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix='/error')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.visuals import bp as visuals_bp
    app.register_blueprint(visuals_bp, url_prefix='/visuals')

    from app.models import User, Role
    from app.auth.forms import LoginForm 
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore=user_datastore,login_form=LoginForm)

    table_builder = TableBuilder()

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Budgy Failure',
                credentials=auth,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/budgy.log',
                                            maxBytes=10240,
                                            backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Budgy startup')

    return app

from app import models,admin_views
