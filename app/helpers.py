from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import User, AccountType
from functools import wraps

def admin_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if User.is_admin(current_user):
      return f(*args, **kwargs)
    else:
      flash("Invalid page", 'danger')
      return redirect(url_for('login'))
  return wrap

def valid_class(form_data):
  if form_data.errors:
    return "is-invalid"
  return ""
