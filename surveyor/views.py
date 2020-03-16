import re
import sys
import traceback
from functools import wraps

from flask import Response, request, render_template, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash

from . import app, db, login_manager
from .models import *
from .helper import *



#################### Web Pages ####################

@app.route('/')
def index_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    else:
        return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/match-teacher')
@login_required
def match_teacher_page():
    # Get all teachers who are not yet matched to a user
    subquery = db.session.query(User.teacher_id).filter(User.teacher_id.isnot(None))
    query_filter = Teacher.id.notin_(subquery)
    teachers = Teacher.query.filter(query_filter).all()
    return render_template('match-teacher.html', teachers=teachers)


@app.route('/dashboard')
@login_required
def dashboard_page():
    if current_user.is_teacher:
        classes = Class.query.filter_by(teacher_id=current_user.teacher.id).all()
        return render_template('teacher-dashboard.html', classes=classes)
    else:
        feedbacks = Feedback.query.filter_by(student_id=current_user.id).all()
        return render_template('student-dashboard.html', feedbacks=feedbacks)


@app.route('/feedback/new')
@login_required
def new_feedback_page():
    if current_user.is_teacher:
        # Ensure only the correct users are accessing
        return redirect(url_for('dashboard_page'))
    
    # Get all classes which the student has no feedback in
    subquery = db.session.query(Feedback.class_id).filter(Feedback.student_id == current_user.id)
    query_filter = Class.id.notin_(subquery)
    classes = Class.query.filter(query_filter).all()
    if not classes:
        # No class left to give feedback
        # TODO: Notify the user about this
        return redirect(url_for('dashboard_page'))

    return render_template('new-feedback.html', classes=classes)



#################### APIs ####################

@app.route('/login', methods=['POST'])
def login():
    '''API for authenticating via the school's system.'''

    # Get form data, defaults to empty string
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    success_flag = False
    is_new_teacher = False

    if all((username, password)): # Data validation
        # Try fetching user from database
        user = User.query.filter_by(school_id=username).first()

        # If user is already in the database, validate credentials directly
        if user and user.authenticate(password):
            success_flag = True
            is_new_teacher = user.is_teacher and user.teacher_id == None

        # New user trying to log in
        elif not user:
            # Authenticate via PowerSchool
            code, name = ykps_auth(username, password)

            if code == 0:
                # User credentials validated, insert into database
                hashed_password = generate_password_hash(password)
                is_new_teacher = not re.match(r's\d{5}', username)
                user = User(school_id=username, name=name, password=hashed_password, is_teacher=is_new_teacher)
                db.session.add(user)
                db.session.commit()
                success_flag = True

    if success_flag:
        # User credentials validated, logs in the user
        login_user(user)

        if is_new_teacher:
            # Teacher logs in for the first time, requests teacher's ID
            return redirect(url_for('match_teacher_page'))
        else:
            return redirect(url_for('dashboard_page'))
    
    else:
        return render_template('login.html', login_msg='Incorrect credentials!')


@app.route('/match-teacher', methods=['POST'])
@login_required
def match_teacher():
    '''API for matching a teacher user to a teacher.'''

    if not (current_user.is_teacher and current_user.teacher_id == None):
        # Ensure only the correct users are accessing
        return redirect(url_for('dashboard_page'))

    # Get form data, defaults to empty string
    teacher_id = request.form.get('teacher-id', '')

    # TODO: Data validation

    # Update user's teacher_id field
    current_user.teacher_id = teacher_id
    db.session.commit()
    return redirect(url_for('dashboard_page'))


@app.route('/feedback/delete', methods=['POST'])
@login_required
def delete_feedback():
    '''API for deleting a feedback.'''

    if current_user.is_teacher:
        # Ensure only the correct users are accessing
        return jsonify({'code': 2})

    # Get form data, defaults to empty string
    feedback_id = request.form.get('id', '')

    # TODO: Data validation

    # Validate data and perform deletion in the database
    feedback = Feedback.query.filter_by(id=feedback_id) # Cannot use get here
    if not feedback:
        return jsonify({'code': 1})
    feedback.delete()
    db.session.commit()
    return jsonify({'code': 0})


@app.route('/feedback/new', methods=['POST'])
@login_required
def new_feedback():
    '''API for creating a new feedback.'''

    if current_user.is_teacher:
        # Ensure only the correct users are accessing
        return render_template(url_for('new_feedback_page'))
    
    feedback_class_id = request.form.get('feedback-class', '')
    feedback_content = request.form.get('feedback-content', '')
    feedback_anonymous = request.form.get('feedback-anonymous', 'off')

    # TODO: Data validation

    feedback_anonymous = True if feedback_anonymous == 'on' else False

    # Performs database insertion
    feedback = Feedback(student_id=current_user.id, class_id=feedback_class_id, content=feedback_content, is_anonymous=feedback_anonymous)
    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for('dashboard_page'))



#################### Misc Views ####################

@login_manager.unauthorized_handler
def unauthorized_access():
    '''Redicts unauthorized users to login page.'''
    return redirect(url_for('login_page'))
