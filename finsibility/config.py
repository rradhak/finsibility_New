import os
import redis

from flask import url_for
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')

    CACHE_TYPE = os.environ.get('CACHE_TYPE')
    CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT')

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    SESSION_TYPE = os.environ.get('SESSION_TYPE')
    SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS'))

    SESSION_PERMANENT= False
    SESSION_USE_SIGNER= True

    STOCK_KEY = os.environ.get('stock_key')
    FINMOD_KEY_1 = os.environ.get('finmod_key')
    FINMOD_KEY_2 = os.environ.get('finmod_key_1')

    TD_ACCOUNT_NBR = os.environ.get('account_number')
    TD_PASSWORD = os.environ.get('password')
    TD_CLIENT_ID = os.environ.get('client_id')

    TWTR_CONSUMER_KEY = os.environ.get('consumer_key')
    TWTR_CONSUMER_SECRET = os.environ.get('consumer_secret')
    TWTR_ACCESS_TOKEN = os.environ.get('access_token')
    TWTR_ACCESS_TOKEN_SECRET = os.environ.get('access_token_secret')



