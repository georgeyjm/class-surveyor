from flask_login import UserMixin
from werkzeug.security import check_password_hash

from surveyor import db, login_manager


db.create_all() # Create tables using the above configuration
