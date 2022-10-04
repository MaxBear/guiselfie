from flask import Flask
from flask_mail import Mail
from flaskext.mysql import MySQL
from flask_login import LoginManager, current_user, login_user
import logging.config

app = Flask(__name__)
app.config.from_envvar('APPLICATION_SETTINGS')

logging_config = app.config['LOGGING_CFG']
logging.config.fileConfig(logging_config)

mail = Mail(app)

mysql = MySQL()
mysql.init_app(app)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.init_app(app)

from .views_selfie import mod_selfie
app.register_blueprint(mod_selfie)
from .views_alerts import mod_alerts
app.register_blueprint(mod_alerts)
from .views_admin import mod_admin
app.register_blueprint(mod_admin)

from selfie.views_common import *
from selfie.views_login import *
from selfie.views_selfie import *
from selfie.views_alerts import *
from selfie.views_admin import *
