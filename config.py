import os
from dotenv import load_dotenv

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

    #SQLAlchemy config variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'budgy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #LANGUAGES = ['en', 'es']
    #MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
