from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def verified_required(f):
    """
    Decorator to restrict access to verified users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.verified:
            flash('Please verify your email to access this feature.', 'warning')
            return redirect(url_for('main.profile'))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """
    Decorator to restrict access to non-authenticated users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('You are already logged in.', 'info')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def payment_required(f):
    """
    Decorator to check if user has payment method setup.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.payment_methods:
            flash('Please add a payment method to continue.', 'warning')
            return redirect(url_for('main.profile'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator to restrict access based on user roles.
    Usage: @role_required('admin', 'manager')
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return wrapper