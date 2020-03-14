from flask_login import UserMixin
from werkzeug.security import check_password_hash

from surveyor import db, login_manager


class Teacher(db.Model):
    '''Model for the teachers table.'''

    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<Teacher {}>'.format(self.name)


class Class(db.Model):
    '''Model for the classes table.'''

    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<Class {}>'.format(self.name)


class User(db.Model, UserMixin):
    '''Model for the users table.'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(128), nullable=False, unique=True)
    name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_teacher = db.Column(db.Boolean, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def authenticate(self, password):
        '''Checks if provided password matches stored password.'''
        return check_password_hash(self.password, password)
    
    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


class Feedback(db.Model):
    '''Model for the feedbacks table.'''

    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Feedback {}>'.format(self.name)


db.create_all() # Initialize tables using the above configuration
