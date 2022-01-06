from flask_bootstrap import Bootstrap
from flask import Flask

"""Testing..."""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from finsibility.config import Config, ProductionConfig
from flask_session import Session

finsy = Flask(__name__)
bootstrap = Bootstrap(finsy)

login = LoginManager(finsy)
login.login_view = 'login'

finsy.config.from_object(ProductionConfig)

server_session = Session(finsy)
db = SQLAlchemy(finsy)

import logging
logging.basicConfig(filename ='logs/finsibility.log', level=logging.DEBUG, format =f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


import finsibility.views

