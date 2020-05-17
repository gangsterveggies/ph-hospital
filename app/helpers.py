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
      return redirect(url_for('index'))
  return wrap

def doctor_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if User.is_doctor(current_user):
      return f(*args, **kwargs)
    else:
      flash("Invalid page", 'danger')
      return redirect(url_for('index'))
  return wrap

def donor_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if User.is_donor(current_user):
      return f(*args, **kwargs)
    else:
      flash("Invalid page", 'danger')
      return redirect(url_for('index'))
  return wrap

def valid_class(form_data):
  if form_data.errors:
    return "is-invalid"
  return ""

def user_filters_url(user_filters, supply_filters, sort_status, user):
  uf = list(user_filters)
  sf = [s['id'] for s in supply_filters]
  try:
    uf.remove(user)
  except:
    pass

  return url_for('donation_log', user='$'.join(uf), supply='$'.join(sf), sortby=sort_status[0], sorttype=sort_status[1])

def supply_filters_url(user_filters, supply_filters, sort_status, supply):
  sf = [s['id'] for s in supply_filters]
  try:
    sf.remove(supply)
  except:
    pass

  return url_for('donation_log', user='$'.join(user_filters), supply='$'.join(sf), sortby=sort_status[0], sorttype=sort_status[1])

def sort_filters_url(user_filters, supply_filters, sort_status, sort_value):
  uf = list(user_filters)
  sf = [s['id'] for s in supply_filters]
  if sort_status[0] == str(sort_value):
    sort_status = (sort_status[0], str(1 - int(sort_status[1])))
  else:
    sort_status = (sort_value, str(0))

  return url_for('donation_log', user='$'.join(uf), supply='$'.join(sf), sortby=sort_status[0], sorttype=sort_status[1])

def sort_icon(sort_status, sort_value):
  if sort_status[0] != str(sort_value):
    return 'fa-sort'
  else:
    if sort_status[1] == "0":
      return 'fa-sort-down'
    else:
      return 'fa-sort-up'
