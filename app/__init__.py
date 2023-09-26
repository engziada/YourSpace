from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from os import getenv
from .helpers import calculate_time_difference,calculate_time_remaining
from pytz import timezone

# Load environment variables from .env file (only during development)
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
# , f'mysql://root:{quote("P@ssw0rd1234567")}@localhost/attendance'
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}
# Set the path for uploaded files (e.g., photos)
app.config['PHOTOS_FOLDER'] = getenv('PHOTOS_FOLDER')
# reCaptcha configuration
app.config['RECAPTCHA_PUBLIC_KEY'] = getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = getenv('RECAPTCHA_PRIVATE_KEY')

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.init_app(app)

# Initialize bcrypt
# bcrypt = bcrypt(app)

# Initialize Bootstrap for Flask
bootstrap = Bootstrap5(app)

# Initialize Flask WTF CSRF Protection
csrf = CSRFProtect(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


###############################################
@app.context_processor
def inject_helpers():
    return dict(calculate_time_remaining=calculate_time_remaining,calculate_time_difference=calculate_time_difference)
###############################################


# Define the fixed timezone (GMT+3)
fixed_timezone = timezone('Etc/GMT-3')

@app.context_processor
def inject_timezone():
    return dict(fixed_timezone=fixed_timezone)


@app.template_filter('timezone')
def timezone_filter(datetime_value, target_timezone):
    if datetime_value:
        return datetime_value.astimezone(target_timezone)#.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ''
###############################################
        
from app import routes
