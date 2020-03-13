import re
import sys
import traceback
from functools import wraps

from flask import Response, request, render_template, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash

from . import app, db, login_manager
from .models import *
from .helper import *



#################### Web Pages ####################

@app.route('/')
def index_page():
    return render_template('base.html')


@app.route('/login')
def login_page():
    return render_template('login.html')



#################### APIs ####################

@app.route('/login', methods=['POST'])
def login():
    '''API for authenticating via the school's system.'''

    # Get form data, defaults to empty string
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    success_flag = False
    new_user_flag = False

    if all((username, password)): # Data validation
        # Try fetching user from database
        user = User.query.filter_by(school_id=username).first()

        # If user is already in the database, validate credentials directly
        if user and user.authenticate(password):
            success_flag = True

        # New user trying to log in
        elif not user:
            # Authenticate via PowerSchool
            code, name = ykps_auth(username, password)

            if code == 0:
                # User credentials validated, insert into database
                hashed_password = generate_password_hash(password)
                is_teacher = not re.match(r's\d{5}', username)
                user = User(school_id=username, name=name, password=hashed_password, is_teacher=is_teacher)
                db.session.add(user)
                db.session.commit()
                new_user_flag = True
                success_flag = True

    if success_flag:
        # User credentials validated, logs in the user
        login_user(user)

        if new_user_flag and is_teacher:
            # Teacher logs in for the first time, requests teacher's ID
            return redirect(url_for('index_page'))
        else:
            return redirect(url_for('dashboard_page'))
    
    else:
        return render_template('login.html', login_msg='Incorrect credentials!')
