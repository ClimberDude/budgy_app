from app.mod_tables.models import TableBuilder

from config import Config
from dotenv import load_dotenv
from flask import Flask, request, current_app

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

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

admin = Admin(name="Budgy")
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate(compare_type=True)
moment = Moment()
login = LoginManager()
login.login_view = 'admin.login'
login.login_message = 'Please log in to access this page.'
security = Security()
table_builder = TableBuilder()

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    admin.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    moment.init_app(app)
    login.init_app(app)

    from app.models import User, Role    

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix='/error')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.visuals import bp as visuals_bp
    app.register_blueprint(visuals_bp, url_prefix='/visuals')

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
