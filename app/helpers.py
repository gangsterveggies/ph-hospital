from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import AccountType
from functools import wraps

def admin_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if current_user.is_admin():
      return f(*args, **kwargs)
    else:
      flash("You need to be an admin")
      return redirect(url_for('login'))
  return wrap

def user_is_admin(user):
  return True
