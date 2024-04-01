from datetime import datetime, timedelta
import random
import string
from turtle import st
from typing import LiteralString
from flask import flash
import pandas as pd
import pytz
from werkzeug.utils import secure_filename
import os
from icecream import ic

def calculate_time_difference(start_time: datetime):
    # Define the fixed timezone (GMT+3)
    fixed_timezone = pytz.timezone('Asia/Riyadh')
    # Get the current datetime in the fixed timezone
    current_time = datetime.now(fixed_timezone)
    # Convert offset-naive previous_time to offset-aware
    # previous_time = fixed_timezone.localize(start_time)
    # previous_time = start_time.astimezone(fixed_timezone)
    previous_time=start_time

    # try:
    # start_time_str= start_time.strftime('%Y-%m-%d %H:%M:%S')
    # start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    diff = current_time - previous_time
    hours = diff.days * 24 + diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    return f'{hours}h {minutes}m'
    # except:
    #     return '0h 0m'


def calculate_time_remaining(start_time: datetime, last_time_remaining: float):
    try:
        # Define the fixed timezone (GMT+3)
        fixed_timezone = pytz.timezone('Asia/Riyadh')
        # Get the current datetime in the fixed timezone
        current_time_utc = datetime.now(pytz.utc)  # Create a timezone-aware datetime object in UTC
        current_time = current_time_utc.astimezone(fixed_timezone)  # Convert to local timezone
        # Convert offset-naive previous_time to offset-aware
        # previous_time = fixed_timezone.localize(start_time)
        previous_time=start_time
        # start_time_str= start_time.strftime('%Y-%m-%d %H:%M:%S')
        # start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        diff = current_time - previous_time
        minutes = round(diff / timedelta(minutes=1), 0)
            
        cur_rem_minutes = float(last_time_remaining * 60)
        new_rem_minutes = cur_rem_minutes - minutes
        new_rem_hours_part = int(new_rem_minutes // 60)
        new_rem_minutes_part= int(new_rem_minutes % 60)
        
        return f'{new_rem_hours_part}h {new_rem_minutes_part}m', new_rem_minutes / 60
    except Exception as e:
        ic(e)
        return '0h 0m',0


# Generate Random Password
def generate_password():
    letters: LiteralString = string.ascii_letters
    numbers: LiteralString = string.digits
    return ''.join(random.choice(letters + numbers) for _ in range(10))


# Print the errors in the form
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form[field].label.text}: {error}", 'danger')


def save_photo(photo_file,app):
    if photo_file:
        # Check if the photo is already saved in the static folder with the same name, if yes, return the photo name
        if (type(photo_file) == str):
            return photo_file

        # Secure the photo name before saving it
        secured_filename = secure_filename(photo_file.filename)
        secured_static_filepath = os.path.join(
            'static', app.config['PHOTOS_FOLDER'], secured_filename)
        secured_physical_filepath = os.path.join(
            app.root_path, secured_static_filepath)

        # Photo URL that will be saved in the database
        photo_url = '/' + \
            os.path.normpath(secured_static_filepath).replace(os.sep, '/')
        # Save the photo in the static folder
        photo_file.save(secured_physical_filepath)
        return photo_url
    else:
        return None


