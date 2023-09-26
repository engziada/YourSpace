# from main import app
# from flask_login import UserMixin
# import os
# from flask_sqlalchemy import SQLAlchemy
# from enum import unique
import datetime
import bcrypt
from app import db, login_manager
from flask_login import UserMixin
from flask import flash, redirect, session, url_for



@login_manager.user_loader
def load_user(user_id):
    # Check if the user exists in the session, if yes, return it
    if 'user' in session:
        user_data = session['user']
        return User.query.get(user_data['id'])
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Error: You must be logged in to access this page.', 'danger')
    return redirect(url_for('login'))


# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False,default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    # employee_data = db.relationship('Employee', back_populates='user', uselist=False)
    # customer_data = db.relationship('Customer', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f"{self.username}, {self.email}, {self.password}, {self.id}"
################################################################################################

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True,nullable=False)
    address = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=True)  # Add the birthdate field
    photo = db.Column(db.String(255), nullable=True)  # Add the photo field
    national_id = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Add the gender field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, unique=True)
    user = db.relationship('User', backref=db.backref('employee', lazy=True))
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    
    def __repr__(self):
        return f"{self.name}"


# Customer Model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=True)  # Add the gender field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, unique=True)
    user = db.relationship('User', backref=db.backref('customer', lazy=True))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    job = db.relationship('Job', backref=db.backref('customer', lazy=True))
    institute_id = db.Column(db.Integer, db.ForeignKey('institute.id'), nullable=True)
    institute = db.relationship('Institute', backref=db.backref('customer', lazy=True))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=True,default=1)
    subscription = db.relationship('Subscription', backref=db.backref('customer', lazy=True))
    subscription_startdate = db.Column(db.DateTime, nullable=True, default=None)
    subscription_remaining = db.Column(db.Numeric(precision=4, scale=2), nullable=True, default=None)  
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    
    def __repr__(self):
        return f"{self.name}"


# Job Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    institutes = db.relationship('Institute', backref='job', lazy=True)

    def __repr__(self):
        return f"{self.name}"



# Institute Model
class Institute(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"{self.name}"


# Space Model
class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(15), nullable=True)
    is_ready = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    photo = db.Column(db.String(255), nullable=True)  # Add the photo field
    capacity = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"{self.name}"


# Package Model
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"{self.name}"


# PricingRule model
class PricingRule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_ = db.Column(db.Integer, nullable=False)
    to_ = db.Column(db.Integer, nullable=False)
    hourly_rate = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    package = db.relationship('Package', backref=db.backref('pricing_rules', lazy=True))

    def __repr__(self):
        return f"{self.from_}:{self.to_} - {self.hourly_rate}"


# Subscription Model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    hours = db.Column(db.Integer, nullable=False, default=5)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    # def __repr__(self):
    #     return f"{self.name} - {self.hours} Hours - {self.price} SR" if self.name != 'None' else f'{self.name}'
    
    
# Log Model
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    period = db.Column(db.String(50), nullable=True)
    total_price = db.Column(db.Float, nullable=True)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    space = db.relationship('Space', backref=db.backref('log', lazy=True))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('log', lazy=True))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('log', lazy=True))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    package = db.relationship('Package', backref=db.backref('log', lazy=True))
    use_subscription = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.start_time} - {self.end_time} - {self.total_price}"

################################################################################################

# EmailSent Model
class EmailSent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipients = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Post Model    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))


####################################################################################################
# Create the default admin user (you can modify this data as needed)
def create_default_admin():
    username = 'admin'
    password = 'admin'
    name='Administrator'
    phone='1234567890'
    email='fake@email.com'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    admin_user = User.query.filter_by(username=username).first()
    if admin_user is None:
        # If the admin user doesn't exist, create it
        admin_user = User(username=username,password_hash=hashed_password,is_admin=True)
        admin_employee = Employee(name=name, phone=phone, email=email, user=admin_user, gender=1)
        
        db.session.add(admin_user)
        db.session.add(admin_employee)
        db.session.commit()
