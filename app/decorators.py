from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Error: Only admins can access this page.', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_function
