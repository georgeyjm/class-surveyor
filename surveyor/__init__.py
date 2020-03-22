from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import app_config


# Initialize flask instances

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config['development'])
app.config.from_pyfile('secrets.py')

db = SQLAlchemy()
db.app = app # Necessary for db.create_all()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


import surveyor.views
