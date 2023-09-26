# from wsgiref.validate import validator
from lib2to3.fixer_base import ConditionalFix
from app.models import *
# from flask import Flask
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import DecimalField,HiddenField, FormField, FieldList, TextAreaField, BooleanField, StringField, EmailField, PasswordField, SubmitField, SelectField, DateField, TimeField, IntegerField, FloatField
from wtforms.validators import DataRequired, EqualTo, Length, Email, NumberRange, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField


def validate_phone_number(form, field):
    # Define your phone number validation logic here
    phone_number = field.data
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]
        if not phone_number.isdigit() or len(phone_number) < 11:
            raise ValidationError('Invalid phone number format')
    elif not phone_number.isdigit() or len(phone_number) != 10:
        raise ValidationError('Invalid phone number format')
    
    
# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
############################################################################################################
# Add User Form
class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin', default=False)
    name= StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), validate_phone_number])
    address = StringField('Address')
    email = EmailField('Email')
    birthdate= DateField('Birthdate')
    national_id= StringField('National ID')
    gender = SelectField('Gender', choices=[(1, 'Male'), (2, 'Female')], coerce=int)
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add User')
    # recaptcha = RecaptchaField()


# Edit User Form
class EditUserForm(FlaskForm):
    # username = StringField('Username', validators=[
    #                        DataRequired(), Length(min=4, max=20)])
    # password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[
    #                                  DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin', default=False)
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    phone = StringField('Phone', validators=[
                        DataRequired(), validate_phone_number])
    address = StringField('Address')
    email = EmailField('Email')
    birthdate = DateField('Birthdate')
    national_id = StringField('National ID')
    gender = SelectField('Gender', choices=[(1, 'Male'), (2, 'Female')], coerce=int)
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save Changes')

############################################################################################################
# Add Customer Form
class AddCustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), validate_phone_number])
    email = EmailField('Email')
    job = QuerySelectField('Job', query_factory=lambda: Job.query.all(), get_label='name')
    institute = QuerySelectField('Institute', query_factory=lambda: Institute.query.all(), get_label='name')
    gender = SelectField('Gender', choices=[(0, ''), (1, 'Male'), (2, 'Female')], coerce=int)
    submit = SubmitField('Add Customer')


# Add Customer External Form
class AddCustomerExternalForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), validate_phone_number])
    email = EmailField('Email')
    job = QuerySelectField('Job', query_factory=lambda: Job.query.all(), get_label='name')
    institute = QuerySelectField('Institute', query_factory=lambda: Institute.query.all(), get_label='name')
    gender = SelectField('Gender', choices=[(0, ''), (1, 'Male'), (2, 'Female')], coerce=int)
    submit = SubmitField('Add Customer')


# Edit Customer Form
class EditCustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)], render_kw={'readonly': True})
    phone = StringField('Phone', validators=[DataRequired(), validate_phone_number], render_kw={'readonly': True})
    email = EmailField('Email')
    job = QuerySelectField('Job', query_factory=lambda: Job.query.all(), get_label='name')
    institute = QuerySelectField('Institute', query_factory=lambda: Institute.query.all(), get_label='name')
    gender = SelectField('Gender', choices=[(0, ''), (1, 'Male'), (2, 'Female')], coerce=int)
# This code snippet creates a subscription field in a form, using a query to populate the options with all available subscriptions from the database. The default value is set to None.
    subscription = QuerySelectField('Subscription', query_factory=lambda: Subscription.query.all(), get_label='name', default=1)
    remaining=HiddenField('Remaining')
    submit = SubmitField('Save Changes')


class SearchCustomerForm(FlaskForm):
    phone = StringField('Phone')
    submit = SubmitField('Search')
############################################################################################################
# Add Space Form
class AddSpaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    area = StringField('Area')
    is_ready = BooleanField('Ready', default=True)
    description = TextAreaField('Description')
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    location = StringField('Location')
    capacity = IntegerField('Capacity',default=1,validators=[NumberRange(min=1)])
    submit = SubmitField('Add Space')
    # recaptcha = RecaptchaField()

# Edit Space Form
class EditSpaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)], render_kw={'readonly': True})
    area = StringField('Area')
    is_ready = BooleanField('Ready', default=True)
    description = TextAreaField('Description')
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    location = StringField('Location')
    capacity = IntegerField('Capacity')
    submit = SubmitField('Save Changes')

############################################################################################################
# Add Package Form
class AddPackageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Add Package')
    # recaptcha = RecaptchaField()


class PackageCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Add Package')

# Edit Package Form
class EditPackageForm(FlaskForm):
    name = StringField('Name', render_kw={'readonly': True})
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Changes')


class PackageDetailsForm(FlaskForm):
    name = StringField('Package Name', render_kw={'readonly': True})
    description = TextAreaField('Description', render_kw={'readonly': True})
    is_active = BooleanField('Active', render_kw={'readonly': True, 'disabled': 'disabled'})
    # spaces = FieldList(FormField(EditSpaceForm), min_entries=0)
    # pricing_rules = TextAreaField('Pricing Rules', render_kw={'readonly': True})

############################################################################################################
# Add Subscription Form
class AddSubscriptionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    hours=IntegerField('Hours',validators=[NumberRange(min=5)])
    price=DecimalField('Price',validators=[NumberRange(min=1)])
    submit = SubmitField('Add Subscription')


class SubscriptionCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    hours=IntegerField('Hours',validators=[NumberRange(min=5)])
    price=DecimalField('Price',validators=[NumberRange(min=1)])
    submit = SubmitField('Add Subscription')


# Edit Subscription Form
class EditSubscriptionForm(FlaskForm):
    name = StringField('Name', render_kw={'readonly': True})
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    hours=IntegerField('Hours',validators=[NumberRange(min=5)])
    price=DecimalField('Price',validators=[NumberRange(min=1)])
    submit = SubmitField('Save Changes')


class SubscriptionDetailsForm(FlaskForm):
    name = StringField('Subscription Name', render_kw={'readonly': True})
    description = TextAreaField('Description', render_kw={'readonly': True})
    is_active = BooleanField('Active', render_kw={'readonly': True, 'disabled': 'disabled'})
    hours=IntegerField('Hours',render_kw={'readonly': True, 'disabled': 'disabled'})
    price=DecimalField('Price',render_kw={'readonly': True, 'disabled': 'disabled'})
    # customers = FieldList(FormField(EditCustomerForm), min_entries=0)

############################################################################################################

# Add PriceingRule Form
class AddPriceingRuleForm(FlaskForm):
    from_ = IntegerField('From (Min)', validators=[DataRequired(), NumberRange(min=1, max=1440)])
    to_ = IntegerField('To (Min)', validators=[DataRequired(), NumberRange(min=1, max=1440)])
    hourly_rate = DecimalField('Cost (SR)', validators=[DataRequired()])
    package = QuerySelectField('Package', query_factory=lambda: Package.query.filter_by(is_active=True).all(), get_label='name')
    submit = SubmitField('Add User')


# Edit PriceingRule Form
class EditPriceingRuleForm(FlaskForm):
    from_ = IntegerField('From (Min)', validators=[DataRequired(), NumberRange(min=1, max=1440)])
    to_ = IntegerField('To (Min)', validators=[DataRequired(), NumberRange(min=1, max=1440)])
    hourly_rate = FloatField('Hourly Rate (SR)', validators=[DataRequired()])
    package = QuerySelectField('Package', query_factory=lambda: Package.query.filter_by(is_active=True).all(), get_label='name')
    submit = SubmitField('Save Changes')
    
############################################################################################################

# Add Job Form
class JobForm(FlaskForm):
    name = StringField('Job', validators=[DataRequired()])
    submit = SubmitField('Add Job')

# Add Institute Form
class InstituteForm(FlaskForm):
    name = StringField('Institute', validators=[DataRequired()])
    job = QuerySelectField('Job', query_factory=lambda: Job.query.all(), get_label='name')
    submit = SubmitField('Add Institute')


############################################################################################################

# Add Log Form
class AddLogForm(FlaskForm):   
    space = QuerySelectField('Space', query_factory=lambda: Space.query.filter_by(is_ready=True).all(), get_label='name')
    customer_search = StringField('Search Customer by Phone')
    customer_details = HiddenField('Customer Details')
    customer_id = HiddenField('Customer ID')
    package = QuerySelectField('Package', query_factory=lambda: Package.query.filter_by(is_active=True).all(), get_label='name')
    use_subscription=BooleanField('Use Subscription', default=False)
    submit = SubmitField('Start')    

# Edit Log Form
class EditLogForm(FlaskForm):
    space = QuerySelectField('Space', query_factory=lambda: Space.query.filter_by(is_ready=True).all(), get_label='name')
    package = QuerySelectField('Package', query_factory=lambda: Package.query.filter_by(is_active = True).all(), get_label='name')
    submit = SubmitField('Start')


############################################################################################################
# Email Template Form
class EmailTemplate(FlaskForm):
    recipients = StringField('Recipients', validators=[DataRequired()])
    subject = StringField('Subject', validators=[
                          DataRequired(), Length(min=1, max=20)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Emails')
