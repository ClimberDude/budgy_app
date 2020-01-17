import os
from dotenv import load_dotenv
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    ADMINS = ['debug.emails@gmail.com']

    ITEMS_PER_PAGE = 10

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    #Scheduler config variables
    # JOBS: [{
    #         'id': 'run_scheduled_transactions',
    #         'func': 'app.scheduled_tasks:apply_repeating_trans',
    #         'trigger': 'interval',
    #         'seconds': 60
    # }]
    SCHEDULER_JOBSTORES = {'default': SQLAlchemyJobStore(url='sqlite:///' + os.path.join(basedir, 'scheduled_trans.db'))}
    SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 20}}
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True

    #SQLAlchemy config variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'budgy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #LANGUAGES = ['en', 'es']
    #MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
