import os
import pytz
from sqlalchemy import and_, func,asc,desc
from app import app, db
from app.forms import * 
from app.models import *
from flask import jsonify, render_template, send_file, session, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
# from flask_mail import Mail, Message
from .helpers import calculate_time_difference, generate_password, flash_errors, save_photo, calculate_time_remaining
import pandas as pd
from app.decorators import admin_required
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename


# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'engziada@gmail.com'
# app.config['MAIL_PASSWORD'] = 'platinumkitten87'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

# mail = Mail(app)


def download_excel(model_name):
    model = globals().get(model_name)
    if not model:
        return None

    items = model.query.all()
    if not items:
        return None

    data = {}
    for column in model.__table__.columns:
        column_name: str = column.name
        if column_name.endswith('_id'):
            column_name_2 = column_name.replace('_id', '')
            data[column_name_2] = [getattr(item, column_name_2) for item in items]
        data[column.name] = [getattr(item, column_name) for item in items]

    df = pd.DataFrame(data)

    excel_file_path = f'{model_name}-{datetime.now().date()}-{datetime.now().time()}.xlsx'
    excel_file_path=secure_filename(excel_file_path)

    # Create an ExcelWriter object
    # excel_writer = pd.ExcelWriter(os.path.join('/home/ziada/YourSpace/app', excel_file_path), engine='xlsxwriter')
    excel_writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
    # Write the DataFrame to Excel
    df.to_excel(excel_writer, sheet_name=f'YourSpace-{model_name}', index=False)
    # Close the ExcelWriter object using close() method
    excel_writer.close()
    # print('+'*50, excel_file_path, '+'*50, sep='\n')

    return excel_file_path


@app.route('/export_to_excel/<model_name>')
@login_required
def export_to_excel(model_name):
    excel_file_path = download_excel(model_name)
    excel_file_path=excel_file_path.replace('app/','')
    # /home/ziada/YourSpace/app/
    # print('+'*50, excel_file_path, '+'*50, sep='\n')
    return send_file(excel_file_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # After successful login, store user data in the session
            session['user'] = {
                'id': user.id,
                'username': user.username,
                'admin': user.is_admin
            }
            return redirect(url_for('home'))
        else:
            flash('Error: Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('login'))


# Home route
@app.route('/')
@app.route('/home')
@login_required
def home():
    return redirect(url_for('logs'))


# About route
@app.route('/about')
def about():
    return render_template('about.html')


# Users route
@app.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of logs per page

    if not current_user.is_admin:
        flash('Error: You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    employees = Employee.query.join(Employee.user).filter(User.username != 'admin').paginate(page=page, per_page=per_page)
    return render_template('users.html', employees=employees)


# Customers route
@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of logs per page

    form = SearchCustomerForm()
    phone_number=None
    customers=None

    if request.method == 'POST' and form.validate_on_submit() and 'search' in request.form:
        phone_number = form.phone.data
        customers = Customer.query.filter(
            Customer.phone.like(f'%{phone_number}%')).order_by(asc(Customer.name)).paginate(page=page, per_page=per_page)  # .all()
        if not customers:
            flash('Customer not found!', 'danger')
            session['search_customer'] = request.form
            return render_template('customers.html', customers=customers, form=form)
    else:
        customers = Customer.query.order_by(asc(Customer.name)).paginate(page=page, per_page=per_page)  # .all()

    return render_template('customers.html', customers=customers,form=form)


# Spaces route
@app.route('/spaces')
@login_required
def spaces():
    spaces = Space.query.all()
    return render_template('spaces.html', spaces=spaces)


# Packages route
@app.route('/packages')
@login_required
def packages():
    packages = Package.query.all()
    return render_template('packages.html', packages=packages)


# Subscriptions route
@app.route('/subscriptions')
@login_required
@admin_required
def subscriptions():
    subscriptions = Subscription.query.all()
    return render_template('subscriptions.html', subscriptions=subscriptions)


# Jobs route
@app.route('/jobs')
@login_required
def jobs():
    jobs =Job.query.all()
    return render_template('jobs.html', jobs=jobs)


# Institutes route
@app.route('/institutes')
@login_required
def institutes():
    institutes = Institute.query.all()
    return render_template('institutes.html', institutes=institutes)


# Spaces route
@app.route('/pricing_rules')
@login_required
def pricing_rules():
    pricing_rules = PricingRule.query.order_by(
        PricingRule.package_id).order_by(PricingRule.from_).all()
    return render_template('pricing_rules.html', pricing_rules=pricing_rules)


# Logs route
@app.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of logs per page

    logs = Log.query.order_by(desc(Log.is_active), desc(Log.start_time)).paginate(page=page, per_page=per_page) #.all()
    return render_template('logs.html', logs=logs)


# Dashboard route
@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    customers = Customer.query.all()

    # Chart (1): Gender Distribution
    gender_data = db.session.query(Customer.gender, db.func.count().label('count')).group_by(Customer.gender).all()
    df = pd.DataFrame(gender_data, columns=['Gender', 'Count'])
    fig = px.pie(df, values='Count', names='Gender', title='Gender Distribution')
    gender_distribution_chart_div = fig.to_html(full_html=False)

    # Chart (2): Job Distribution
    query = db.session.query(Job.name, Institute.name, db.func.count().label('count'))\
        .join(Customer, Customer.job_id == Job.id)\
        .join(Institute, Customer.institute_id == Institute.id)\
        .group_by(Job.name, Institute.name).all()
    df = pd.DataFrame(query, columns=['Job', 'Institute', 'Count'])
    fig = px.bar(df, x='Job', y='Count', color='Institute',title='Job and Institute Distribution', labels={'Job': 'Job Name'})
    job_institute_chart_div = fig.to_html(full_html=False)

    # Chart (3): Subscription Distribution
    # subscription_data = db.session.query(
    #     (datetime.now() - Customer.subscription_startdate).label('duration')).filter(Customer.subscription_startdate.isnot(None)).all()
    # duration_values = [row.duration for row in subscription_data]
    # df = pd.DataFrame({'Duration': duration_values})
    # fig = px.histogram(df, x='Duration', title='Subscription Duration Histogram',labels={'Duration': 'Duration (Days)'})
    # histogram_div = fig.to_html(full_html=False)

    # Chart (3): Subscriptions Per Month
    subscription_data = db.session.query(
        Subscription.name,
        db.func.DATE_FORMAT(Customer.subscription_startdate, '%b %Y').label('month'),
        db.func.count().label('count'),
        db.func.DATE_FORMAT(Customer.subscription_startdate, '%a %d').label('day'))\
            .join(Customer, Customer.subscription_id == Subscription.id)\
            .group_by(Subscription.name, 'month').all()
    df = pd.DataFrame(subscription_data, columns=['Subscription', 'Month', 'Count','Day'])
    fig = px.line(df, x='Month', y='Count', color='Subscription',text='Day',
                  title='Subscriptions Per Month',
                  labels={'Month': 'Month', 'Count': 'Number of Subscriptions'})
    fig.update_traces(textposition="bottom right")
    subscriptions_per_month_chart_div = fig.to_html(full_html=False)

    # Chart (4): Monthly Customer Growth
    customer_growth_data = db.session.query(
        db.func.DATE_FORMAT(Customer.creation_date, '%b %Y').label('month'),
        db.func.count().label('count'),
        db.func.DATE_FORMAT(Customer.creation_date, '%a %d').label('day')
    ).group_by('month').order_by('month').all()
    df = pd.DataFrame(customer_growth_data, columns=['Month', 'Customer Count','Day'])
    fig = px.line(df, x='Month', y='Customer Count',text='Day', title='Monthly Customer Growth',
                  labels={'Month': 'Month', 'Customer Count': 'Number of Customers'})
    fig.update_traces(textposition="bottom right")
    customer_growth_chart_div = fig.to_html(full_html=False)

    # Chart (5): Gender vs. Job Heatmap
    # gender_job_data = db.session.query(
    #     Customer.gender,
    #     Job.name.label('job'),
    #     db.func.count().label('count')
    # ).join(Job).group_by(Customer.gender, 'job').all()
    # df = pd.DataFrame(gender_job_data, columns=['Gender', 'Job', 'Count'])
    # fig = px.imshow(df.pivot_table(index='Gender', columns='Job', values='Count'),
    #                 x=df['Job'].unique(), y=df['Gender'].unique(),
    #                 color_continuous_scale='Viridis', title='Gender vs. Job Heatmap')
    # fig.update_xaxes(title_text='Job')
    # fig.update_yaxes(title_text='Gender')
    # gender_job_heatmap_div = fig.to_html(full_html=False)

    # Chart (5): Usage Over Time
    usage_data = db.session.query(
        db.func.DATE_FORMAT(Log.start_time, '%b %Y').label('month'),  # You can use 'week' instead of 'month'
        db.func.count().label('count'),
        db.func.DATE_FORMAT(Log.start_time, '%a %d').label('day')
    ).group_by('month').order_by('month').all()
    df = pd.DataFrame(usage_data, columns=['Month', 'Usage Count','Day'])
    fig = px.line(df, x='Month', y='Usage Count', text='Day',title='Usage Over Time',
                  labels={'Month': 'Month', 'Usage Count': 'Usage Count'})
    fig.update_traces(textposition="bottom right")
    usage_chart_div = fig.to_html(full_html=False)

    # Chart (6): Revenue Analysis
    revenue_data = db.session.query(
        db.func.DATE_FORMAT(Log.start_time, '%b %Y').label('month'),  # You can use 'week' instead of 'month'
        db.func.sum(Log.total_price).label('total_revenue')
    ).group_by('month').order_by('month').all()
    df = pd.DataFrame(revenue_data, columns=['Month', 'Total Revenue'])
    fig = px.bar(df, x='Month', y='Total Revenue', title='Revenue Analysis',
                 labels={'Month': 'Month', 'Total Revenue': 'Total Revenue'})
    revenue_chart = fig.to_html(full_html=False)

    # Chart (7): Customer Behavior
    customer_behavior_data = db.session.query(
        Log.customer_id,
        db.func.count().label('log_count')
    ).group_by(Log.customer_id).all()
    df = pd.DataFrame(customer_behavior_data, columns=['Customer ID', 'Log Count'])
    fig = px.bar(df, x='Log Count', y='Customer ID', title='Customer Behavior',
                 labels={'Customer ID': 'Number of Customers','Log Count': 'Number of Logs'})
    customer_behavior_chart = fig.to_html(full_html=False)

    # Chart (8): Package Analysis
    package_data = db.session.query(
        Package.name.label('Package Name'),  # Include package names
        db.func.count().label('Count')
    ).join(Log).group_by(Package.name).all()
    df = pd.DataFrame(package_data, columns=['Package Name', 'Count'])
    fig = px.pie(df, names='Package Name', values='Count', title='Package Analysis')
    package_chart = fig.to_html(full_html=False)

    # Chart (9): Subscription Analysis
    subscription_data = db.session.query(
        Customer.subscription_id,
        Subscription.name.label('Subscription Name'),  # Include subscription names
        db.func.count().label('Count')
    ).join(Log).join(Subscription).filter(Log.use_subscription == True).group_by(Customer.subscription_id, 'Subscription Name').all()
    df = pd.DataFrame(subscription_data, columns=['Subscription ID', 'Subscription Name', 'Count'])
    fig = px.pie(df, names='Subscription Name', values='Count', title='Subscription Analysis')
    subscription_chart = fig.to_html(full_html=False)



    return render_template('dashboard.html', 
                        chart1=gender_distribution_chart_div,
                        chart2=job_institute_chart_div,
                        chart3=subscriptions_per_month_chart_div,
                        chart4=customer_growth_chart_div,
                        chart5=usage_chart_div,
                        chart6=revenue_chart,
                        chart7=customer_behavior_chart,
                        chart8=package_chart,
                        chart9=subscription_chart,
                        )

############################################################################################################
# Add user route
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        is_admin = form.is_admin.data
        name = form.name.data
        phone = form.phone.data
        address = form.address.data
        email = form.email.data
        birthdate = form.birthdate.data
        national_id = form.national_id.data
        gender = form.gender.data
        photo_file = form.photo.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Error: Username already exists.', 'danger')
            session['add_user'] = request.form
            return render_template('add_user.html', form=form)

        existing_email = Employee.query.filter_by(email=email).first()
        if existing_email:
            flash('Error: Email already exists.', 'danger')
            session['add_user'] = request.form
            return render_template('add_user.html', form=form)

        existing_phone = Employee.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Error: Phone nnumber already exists.', 'danger')
            session['add_user'] = request.form
            return render_template('add_user.html', form=form)

        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        user_id = new_user.id
        new_employee = Employee(name=name, phone=phone, address=address, email=email,
                                birthdate=birthdate, national_id=national_id, gender=gender, photo=save_photo(photo_file,app), user_id=user_id)
        db.session.add(new_employee)
        db.session.commit()

        flash('Done: New user added successfully!', 'success')
        return redirect(url_for('users'))
    else:
        session['add_user'] = request.form
        return render_template('add_user.html', form=form)


# Edit user route
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    employee = Employee.query.filter_by(user_id=user_id).first()
    form = EditUserForm(obj=employee)
    if form.validate_on_submit():
        # username = form.username.data
        # password = form.password.data
        user.is_admin = form.is_admin.data
        employee.name = form.name.data
        employee.phone = form.phone.data
        employee.address = form.address.data
        employee.email = form.email.data
        employee.birthdate = form.birthdate.data
        employee.national_id = form.national_id.data
        employee.gender = form.gender.data
        employee.photo = save_photo(form.photo.data,app)
        db.session.commit()
        flash('Done: User details updated successfully!', 'success')
        return redirect(url_for('users'))
    else:
        session['edit_user'] = request.form
        return render_template('edit_user.html', form=form, employee=employee)


# Delete user route
@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    employee=Employee.query.filter_by(user_id=user_id).first()
    db.session.delete(user)
    db.session.delete(employee)
    db.session.commit()
    flash('Done: User deleted successfully!', 'success')
    return redirect(url_for('users'))


# Change Password route
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            logout()
            return redirect(url_for('login'))
        else:
            flash('Old password is incorrect.', 'danger')

    return render_template('change_password.html', form=form)


# Reset Password route
@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = generate_password()
    user.set_password(new_password)
    db.session.commit()
    return jsonify(new_password)

############################################################################################################

# Add customer route
@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = AddCustomerForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            phone = form.phone.data
            email = form.email.data
            institute = form.institute.data
            job = form.job.data
            gender = form.gender.data

            
            existing_email = Customer.query.filter_by(email=email).first()
            if existing_email:
                flash('Error: Email already exists.', 'danger')
                session['add_customer'] = request.form
                return render_template('add_customer.html', form=form)
            existing_phone = Customer.query.filter_by(phone=phone).first()
            if existing_phone:
                flash('Error: Phone number already exists.', 'danger')
                session['add_customer'] = request.form
                return render_template('add_customer.html', form=form)


            gender_label = dict(form.gender.choices).get(gender)  # Get the label
            new_customer = Customer(name=name, phone=phone, email=email, job=job, institute=institute, gender=gender_label)
            db.session.add(new_customer)
            db.session.commit()

            flash('Done: New customer added successfully!', 'success')
            return redirect(url_for('customers'))
        else:
            flash_errors(form)
            session['add_customer'] = request.form
            return render_template('add_customer.html', form=form)
    return render_template('add_customer.html', form=form)



# Edit customer route
@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = EditCustomerForm(obj=customer)
    gender_label = dict(form.gender.choices).get(form.gender.data)  # Get the label
    text_to_value = {choice[1]: choice[0] for choice in form.gender.choices}
    selected_value = text_to_value.get(customer.gender, None)
    form.gender.data=selected_value
    form.remaining=customer.subscription_remaining
    
    if request.method == 'POST':        
        if form.validate_on_submit():
            # Check if subscription is not 'None'
            if form.subscription.data.id != 1:
                customer.subscription_startdate = datetime.now()
                customer.subscription_remaining = form.subscription.data.hours
            
            form.populate_obj(customer)
            customer.gender = gender_label
            db.session.commit()
            flash('Done: Customer details updated successfully!', 'success')
            return redirect(url_for('customers'))
        else:
            flash_errors(form)
            session['edit_customer'] = request.form
            return render_template('edit_customer.html', form=form)
    return render_template('edit_customer.html', form=form)


# Delete customer route
@app.route('/delete_customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('Done: Customer deleted successfully!', 'success')
        return redirect(url_for('customers'))
    except:
        flash('Error: Customer cannot be deleted!', 'danger')
        return redirect(url_for('customers'))
    

# Add customer by customer route
@app.route('/add_customer_external', methods=['GET', 'POST'])
def add_customer_external():
    form = AddCustomerExternalForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            phone = form.phone.data
            email = form.email.data
            institute = form.institute.data
            job = form.job.data
            gender = form.gender.data

            
            existing_email = Customer.query.filter_by(email=email).first()
            if existing_email:
                flash('Error: Email already exists.', 'danger')
                session['add_customer'] = request.form
                return render_template('add_customer_external.html', form=form)
            existing_phone = Customer.query.filter_by(phone=phone).first()
            if existing_phone:
                flash('Error: Phone number already exists.', 'danger')
                session['add_customer'] = request.form
                return render_template('add_customer_external.html', form=form)


            gender_label = dict(form.gender.choices).get(gender)  # Get the label
            new_customer = Customer(name=name, phone=phone, email=email, job=job, institute=institute, gender=gender_label)
            db.session.add(new_customer)
            db.session.commit()

            flash('You may proceed to reception desk to reserve YOUR SPACE.', 'info')
            return redirect(url_for('about'))
        else:
            flash_errors(form)
            session['add_customer_external'] = request.form
            return render_template('add_customer_external.html', form=form)
    return render_template('add_customer_external.html', form=form)



@app.route('/get_institutes/<int:job_id>', methods=['GET'])
def get_institutes(job_id):
    job = Job.query.get_or_404(job_id)
    institutes = [{'id': institute.id, 'name': institute.name}for institute in job.institutes]
    if not institutes:
        empty_institutes = Institute(name='None', job=job)
        db.session.add(empty_institutes)
        db.session.commit()
        institutes = [{'id': empty_institutes.id, 'name': empty_institutes.name}]
    return jsonify(institutes)

############################################################################################################
# Add space route
@app.route('/add_space', methods=['GET', 'POST'])
@login_required
@admin_required
def add_space():
    form = AddSpaceForm()
    if form.validate_on_submit():
        name = form.name.data
        area = form.area.data
        is_ready = form.is_ready.data
        description = form.description.data
        photo_file = form.photo.data
        capacity = form.capacity.data
        location = form.location.data
        
        existing_name = Space.query.filter_by(name=name).first()
        if existing_name:
            flash('Error: Room name already exists.', 'danger')
            session['add_space'] = request.form
            return render_template('add_space.html', form=form)

        new_space = Space(name=name, area=area, is_ready=is_ready, description=description,
                          photo=save_photo(photo_file,app), capacity=capacity, location=location)

        db.session.add(new_space)
        db.session.commit()

        flash('Done: New space added successfully!', 'success')
        return redirect(url_for('spaces'))
    else:
        session['add_space'] = request.form
        return render_template('add_space.html', form=form)


# Edit Space route
@app.route('/edit_space/<int:space_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_space(space_id):
    space = Space.query.get_or_404(space_id)
    form = EditSpaceForm(obj=space)
    if form.validate_on_submit():
        space.area = form.area.data
        space.is_ready = form.is_ready.data
        space.description = form.description.data
        space.photo = save_photo(form.photo.data,app)
        space.capacity = form.capacity.data
        space.location = form.location.data

        db.session.commit()
        flash('Done: Space details updated successfully!', 'success')
        return redirect(url_for('spaces'))
    else:
        session['edit_space'] = request.form
        return render_template('edit_space.html', form=form, space=space)


# Delete Space route
@app.route('/delete_space/<int:space_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_space(space_id):
    try:
        space = Space.query.get_or_404(space_id)
        db.session.delete(space)
        db.session.commit()
        flash('Done: Space deleted successfully!', 'success')
        return redirect(url_for('spaces'))
    except:
        flash('Error: Space cannot be deleted!', 'danger')
        return redirect(url_for('spaces'))

############################################################################################################
# Add Package route
@app.route('/add_package', methods=['GET', 'POST'])
@login_required
@admin_required
def add_package():
    form = PackageCreateForm()
    if form.validate_on_submit():
        name = form.name.data
        is_active = form.is_active.data
        description = form.description.data

        existing_name = Package.query.filter_by(name=name).first()
        if existing_name:
            flash('Error: Package name already exists.', 'danger')
            session['add_package'] = request.form
            return render_template('add_package.html', form=form)

        new_package = Package(name=name, is_active=is_active, description=description)
        db.session.add(new_package)
        db.session.commit()

        flash('Done: New Package added successfully!', 'success')
        return redirect(url_for('packages'))
    else:
        session['add_package'] = request.form
        return render_template('add_package.html', form=form)


# Edit Package route
@app.route('/edit_package/<int:package_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = EditPackageForm(obj=package)
    if form.validate_on_submit():
        package.is_active = form.is_active.data
        package.description = form.description.data

        db.session.commit()
        flash('Done: Package details updated successfully!', 'success')
        return redirect(url_for('packages'))
    else:
        session['edit_package'] = request.form
        return render_template('edit_package.html', form=form, package=package)


# Delete Package route
@app.route('/delete_package/<int:package_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_package(package_id):
    try:
        package = Package.query.get_or_404(package_id)
        db.session.delete(package)
        db.session.commit()
        flash('Done: Package deleted successfully!', 'success')
        return redirect(url_for('packages'))
    except:
        flash('Error: Package cannot be deleted!', 'danger')
        return redirect(url_for('packages'))


# Package details route
@app.route('/package_details/<int:package_id>')
@login_required
def package_details(package_id):
    package = Package.query.get_or_404(package_id)

    form = PackageDetailsForm()
    form.name.data = package.name
    form.description.data = package.description

    return render_template('details_package.html', form=form, package=package)

############################################################################################################

# Add Subscription route
@app.route('/add_subscription', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subscription():
    form = SubscriptionCreateForm()
    if form.validate_on_submit():
        name = form.name.data
        is_active = form.is_active.data
        description = form.description.data
        hours= form.hours.data
        price= form.price.data
        
        existing_name = Subscription.query.filter_by(name=name).first()
        if existing_name:
            flash('Error: Subscription name already exists.', 'danger')
            session['add_subscription'] = request.form
            return render_template('add_subscription.html', form=form)
        
        #Check if the subscription has any existing subscription
        first_subscription = Subscription.query.first()
        if not first_subscription:
            none_subscription = Subscription(id=1, name='None', is_active=True, description='Do NOT delete this one', hours=0, price=0)
            db.session.add(none_subscription)
            db.session.commit()
                
        
        new_subscription = Subscription(name=name, is_active=is_active, description=description, hours=hours, price=price)
        db.session.add(new_subscription)
        db.session.commit()

        flash('Done: New Subscription added successfully!', 'success')
        return redirect(url_for('subscriptions'))
    else:
        session['add_subscription'] = request.form
        return render_template('add_subscription.html', form=form)


# Edit Subscription route
@app.route('/edit_subscription/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    form = EditSubscriptionForm(obj=subscription)
    if form.validate_on_submit():
        subscription.is_active = form.is_active.data
        subscription.description = form.description.data
        subscription.hours = form.hours.data
        subscription.price = form.price.data

        db.session.commit()
        flash('Done: Subscription details updated successfully!', 'success')
        return redirect(url_for('subscriptions'))
    else:
        session['edit_subscription'] = request.form
        return render_template('edit_subscription.html', form=form, subscription=subscription)


# Delete Subscription route
@app.route('/delete_subscription/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_subscription(subscription_id):
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        db.session.delete(subscription)
        db.session.commit()
        flash('Done: Subscription deleted successfully!', 'success')
        return redirect(url_for('subscriptions'))
    except:
        flash('Error: Subscription cannot be deleted!', 'danger')
        return redirect(url_for('subscriptions'))


# Subscription details route
@app.route('/subscription_details/<int:subscription_id>')
@login_required
def subscription_details(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)

    form = SubscriptionDetailsForm()
    form.name.data = subscription.name
    form.description.data = subscription.description
    form.hours.data = subscription.hours
    form.price.data = subscription.price
    form.is_active.data = subscription.is_active
    # form.customers.data = subscription.customers

    return render_template('details_subscription.html', form=form, subscription=subscription)
############################################################################################################

# Add Pricing Rules route
@app.route('/add_pricing_rule', methods=['GET', 'POST'])
@login_required
@admin_required
def add_pricing_rule():
    form = AddPriceingRuleForm()
    # Get the list of packages for the SelectField in the form
    form.package.choices = [(package.id, package.name)for package in Package.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        # Check that from_ is before to_
        if form.from_.data > form.to_.data:
            flash("(From) time must be before (To) time.", 'error')
            session['add_pricing_rule'] = request.form
            return render_template('add_pricing_rule.html', form=form)
        
        # Check for overlapping periods with previous rules
        overlapping_rule = PricingRule.query.filter(and_(PricingRule.package_id == form.package.data.id,
                                                         PricingRule.from_ < form.to_.data,
                                                         PricingRule.to_ > form.from_.data)).first()
        if overlapping_rule:
            flash("Edited rule overlaps with a previous rule.", 'error')
            session['add_pricing_rule'] = request.form
            return render_template('add_pricing_rule.html', form=form)

        new_pricing_rule = PricingRule(
            from_=form.from_.data,
            to_=form.to_.data,
            hourly_rate=form.hourly_rate.data,
            package=form.package.data
        )

        db.session.add(new_pricing_rule)
        db.session.commit()

        return redirect(url_for('pricing_rules'))
    else:
        session['add_pricing_rule'] = request.form
        return render_template('add_pricing_rule.html', form=form)


# Edit Pricing Rules route
@app.route('/edit_pricing_rule/<int:pricing_rule_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_pricing_rule(pricing_rule_id):
    pricing_rule = PricingRule.query.get_or_404(pricing_rule_id)
    form = EditPriceingRuleForm(obj=pricing_rule)

    # Get the list of packages for the SelectField in the form
    form.package.choices = [(package.id, package.name)for package in Package.query.all()]   

    if request.method == 'POST' and form.validate_on_submit():
        # Check that from_ is before to_
        if form.from_.data > form.to_.data:
            flash("(From) time must be before (To) time.", 'error')
            session['edit_pricing_rule'] = request.form
            return render_template('edit_pricing_rule.html', form=form)

        # Check for overlapping periods with previous rules
        overlapping_rule = PricingRule.query.filter(and_(PricingRule.id != pricing_rule.id,
                                                         PricingRule.package_id == pricing_rule.package.id,
                                                         PricingRule.from_ < form.to_.data,
                                                         PricingRule.to_ > form.from_.data)).first()
        if overlapping_rule:
            flash("Edited rule overlaps with a previous rule.", 'error')
            session['edit_pricing_rule'] = request.form
            return render_template('edit_pricing_rule.html', form=form)


        pricing_rule.from_ = form.from_.data
        pricing_rule.to_ = form.to_.data
        pricing_rule.hourly_rate = form.hourly_rate.data
        pricing_rule.package = form.package.data
        
        db.session.commit()
        return redirect(url_for('pricing_rules'))
    else:
        session['edit_pricing_rule'] = request.form
        return render_template('edit_pricing_rule.html', form=form)


# Delete Pricing Rules route
@app.route('/delete_pricing_rule/<int:pricing_rule_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_pricing_rule(pricing_rule_id):
    try:
        pricing_rule = PricingRule.query.get_or_404(pricing_rule_id)
        db.session.delete(pricing_rule)
        db.session.commit()
        return redirect(url_for('pricing_rules'))
    except:
        flash('Error: Pricing rule cannot be deleted!', 'danger')
        return redirect(url_for('pricing_rules'))
    
##############################################################################################################

# Add Log Route
@app.route('/add_log', methods=['GET', 'POST'])
@login_required
def add_log():    
    form = AddLogForm()
    if request.method == 'POST' and form.validate_on_submit():
        if 'search' in request.form:
            phone_number = form.customer_search.data
            if not phone_number:
                flash('Please enter a phone number!', 'danger')
                session['add_log'] = request.form
                return render_template('add_log.html', form=form)
            customer = Customer.query.filter(
                Customer.phone.like(f'%{phone_number}%')).first()
            if customer:
                form.customer_details.data = customer
                form.customer_id.data = customer.id
            else:
                flash('Customer not found!', 'danger')
                session['add_log'] = request.form
                return render_template('add_log.html', form=form)

        elif 'confirm' in request.form:
            # Define the fixed timezone (GMT+3)
            fixed_timezone = pytz.timezone('Asia/Riyadh')
            # Get the current datetime in the fixed timezone
            current_time = datetime.now(fixed_timezone)
            
            sel_customer = Customer.query.filter_by(id=form.customer_id.data).first()
            existing_log = Log.query.filter_by(customer=sel_customer, is_active=True).first()
            if existing_log:
                flash(f'Error: Customer already registered in another space ({existing_log.space.name})', 'danger')
                session['add_log'] = request.form
                return redirect(url_for('logs'))
        
            new_log = Log(
                space=form.space.data,
                customer=sel_customer,
                employee=Employee.query.filter_by(user_id=current_user.id).first(),
                is_active=True,
                start_time=current_time,
                package=form.package.data,
                use_subscription=form.use_subscription.data

            )
            db.session.add(new_log)
            db.session.commit()
            return redirect(url_for('logs'))
    else:
        session['add_log'] = request.form
        return render_template('add_log.html', form=form)

    return render_template('add_log.html', form=form)


# Edit Log Route
@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_log(log_id):
    log = Log.query.get_or_404(log_id)
    form = EditLogForm(obj=log)

    if request.method == 'POST' and form.validate_on_submit():
        log.space = form.space.data

        db.session.commit()
        return redirect(url_for('logs'))

    return render_template('edit_log.html', form=form)


# Delete Log Route
@app.route('/delete_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_log(log_id):
    try:
        log = Log.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return redirect(url_for('logs'))
    except:
        flash('Error: Log cannot be deleted!', 'danger')
        return redirect(url_for('logs'))


# Checkout
@app.route('/checkout/<int:log_id>', methods=['GET', 'POST'])
@login_required
def checkout(log_id:int):
    log = Log.query.get_or_404(log_id)

    # Get data from the log
    start_time=log.start_time
    # Define the fixed timezone (GMT+3)
    fixed_timezone = pytz.timezone('Asia/Riyadh')
    # Get the current datetime in the fixed timezone
    current_time = datetime.now(fixed_timezone)
    # Convert offset-naive previous_time to offset-aware
    previous_time = fixed_timezone.localize(start_time)

    diff = current_time - previous_time
    # hours = round(diff / timedelta(hours=1), 2)
    minutes = round(diff / timedelta(minutes=1), 0)
    # cieled_hours = math.ceil(hours)
    period = calculate_time_difference(start_time)

    selected_rule=None

    if log.use_subscription:
        # cur_rem_minutes = float(log.customer.subscription_remaining * 60)
        # if minutes > cur_rem_minutes: overflow=True
        # new_rem_minutes = cur_rem_minutes - minutes
        # new_rem_hours_part = int(new_rem_minutes // 60)
        # new_rem_minutes_part= int(new_rem_minutes % 60)
        remaining_time, remaining_hours = calculate_time_remaining(start_time, log.customer.subscription_remaining)
        
        result = f'''
                <div class="table-container" style="text-align: left;">
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Customer Name:</div>
                        <div class="table-data" style="font-weight: lighter;">{log.customer.name}</div>
                    </div>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Arrival Time:</div>
                        <div class="table-data" style="font-weight: lighter;">{previous_time.strftime('%d/%m/%Y, %H:%M')}</div>
                    </div>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Leave Time:</div>
                        <div class="table-data" style="font-weight: lighter;">{current_time.strftime('%d/%m/%Y, %H:%M')}</div>
                    </div>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Total Stay:</div>
                        <div class="table-data" style="font-weight: lighter;">{period}</div>
                    </div>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Checkout Method:</div>
                        <div class="table-data" style="font-weight: lighter;">Subscription</div>
                    </div>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Subscription:</div>
                        <div class="table-data" style="font-weight: lighter;">{log.customer.subscription.name}</div>
                    </div>
                    <hr>
                    <div class="table-row" style="border: none;">
                        <div class="table-header">Remaining After:</div>
                        <div class="table-data" style="font-weight: lighter;">{remaining_time}</div>
                    </div>
                </div>
            '''
        session['Checkout-'+str(log.id)] = {
            'log_id': log.id,
            'start_time': previous_time,
            'current_time': current_time,
            'period': period,
            'cost':0,
            'remaining': remaining_hours
        }
    else:
        for rule in log.package.pricing_rules:
            # print('+'*50, rule.from_, minutes,rule.to_,'+'*50, sep='\n')
            if rule.from_ <= minutes <= rule.to_:
                selected_rule = rule
                break
                
        if selected_rule:
            cost = selected_rule.hourly_rate
            result = f'''
                    <div class="table-container" style="text-align: left;">
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Customer Name:</div>
                            <div class="table-data" style="font-weight: lighter;">{log.customer.name}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Arrival Time:</div>
                            <div class="table-data" style="font-weight: lighter;">{previous_time.strftime('%d/%m/%Y, %H:%M')}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Leave Time:</div>
                            <div class="table-data" style="font-weight: lighter;">{current_time.strftime('%d/%m/%Y, %H:%M')}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Total Stay:</div>
                            <div class="table-data" style="font-weight: lighter;">{minutes} Minutes</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Checkout Method:</div>
                            <div class="table-data" style="font-weight: lighter;">Cash</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Package:</div>
                            <div class="table-data" style="font-weight: lighter;">{log.package.name}</div>
                        </div>
                        <hr>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Total Cost:</div>
                            <div class="table-data" style="font-weight: lighter;">{cost} SR</div>
                        </div>
                    </div>
                    '''
        else:
            cost = 0
            result = f'''
                    <div class="table-container" style="text-align: left;">
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Customer Name:</div>
                            <div class="table-data" style="font-weight: lighter;">{log.customer.name}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Arrival Time:</div>
                            <div class="table-data" style="font-weight: lighter;">{previous_time.strftime('%d/%m/%Y, %H:%M')}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Leave Time:</div>
                            <div class="table-data" style="font-weight: lighter;">{current_time.strftime('%d/%m/%Y, %H:%M')}</div>
                        </div>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Total Stay:</div>
                            <div class="table-data" style="font-weight: lighter;">{minutes} Minutes</div>
                        </div>
                        <hr>
                        <div class="table-row" style="border: none;">
                            <div class="table-header">Free of Caharge</div>
                        </div>
                    </div>
                    '''
        
        session['Checkout-'+str(log.id)] = {
            'log_id': log.id,
            'start_time': previous_time,
            'current_time': current_time,
            'period': period,
            'cost': cost
        }

    return jsonify({'result': result})
    

# Stop Log Route
@app.route('/stop_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def stop_log(log_id):
    log = Log.query.get_or_404(log_id)
    fixed_timezone = pytz.timezone('Asia/Riyadh')

    if session.get('Checkout-'+str(log.id)):
        checkout_record:dict= session.pop('Checkout-'+str(log.id))
        log.total_price = checkout_record.get('cost')
        log.end_time = (checkout_record.get('current_time')).astimezone(fixed_timezone)
        log.period = checkout_record.get('period')
        log.is_active = False
        if log.use_subscription:
            log.customer.subscription_remaining = checkout_record.get('remaining')
        db.session.commit()
        return redirect(url_for('logs'))
    else:
        flash('Error: Log not found!', 'danger')
        return redirect(url_for('logs'))
    
##############################################################################################################

# Add Job route
@app.route('/add_job', methods=['GET', 'POST'])
@login_required
@admin_required
def add_job():
    form = JobForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_job = Job(name=form.name.data)
        db.session.add(new_job)
        db.session.commit()

        return redirect(url_for('jobs'))
    else:
        session['add_job'] = request.form
        return render_template('add_job.html', form=form)


# Edit Job route
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = JobForm(obj=job)
    if request.method == 'POST' and form.validate_on_submit():
        job.name = form.name.data
        db.session.commit()
        return redirect(url_for('jobs'))
    else:
        session['edit_job'] = request.form
        return render_template('edit_job.html', form=form)


# Delete Job route
@app.route('/delete_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return redirect(url_for('jobs'))
    except:
        flash('Error: Job cannot be deleted!', 'danger')
        return redirect(url_for('jobs'))

##############################################################################################################

# Add Institute route
@app.route('/add_institute', methods=['GET', 'POST'])
@login_required
@admin_required
def add_institute():
    form = InstituteForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_institute = Institute(name=form.name.data,job=form.job.data)
        db.session.add(new_institute)
        db.session.commit()

        return redirect(url_for('institutes'))
    else:
        session['add_institute'] = request.form
        return render_template('add_institute.html', form=form)


# Edit Institute route
@app.route('/edit_institute/<int:institute_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_institute(institute_id):
    institute = Institute.query.get_or_404(institute_id)
    form = InstituteForm(obj=institute)
    if request.method == 'POST' and form.validate_on_submit():
        institute.name = form.name.data
        institute.job = form.job.data
        db.session.commit()
        return redirect(url_for('institutes'))
    else:
        session['edit_institute'] = request.form
        return render_template('edit_institute.html', form=form)


# Delete Institute route
@app.route('/delete_institute/<int:institute_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_institute(institute_id):
    try:
        institute = Institute.query.get_or_404(institute_id)
        db.session.delete(institute)
        db.session.commit()
        return redirect(url_for('institutes'))
    except:
        flash('Error: Institute cannot be deleted!', 'danger')
        return redirect(url_for('institutes'))
    
##############################################################################################################

@app.errorhandler(404)
def not_found_error(error):
    flash('Error: Page not found!', 'danger')
    return redirect(url_for('home'))


@app.errorhandler(500)
def internal_error():
    flash('Error: Internal server error!', 'danger')
    db.sesssion.rollback()
    return redirect(url_for('home'))
