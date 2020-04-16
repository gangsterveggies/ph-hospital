from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, CreateAccountForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, AccountType, Hospital
from app.helpers import admin_required
from app.email import send_password_reset_email, send_create_account_email
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
  hospitals = Hospital.query.all()
  return render_template('index.html', title='Home', hospitals=hospitals)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password', 'danger')
      return redirect(url_for('login'))
    login_user(user, remember=True)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('index')
    return redirect(next_page)
  return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
@admin_required
def create_account():
  form = CreateAccountForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    password = User.random_password()
    user.set_password(password)
    try:
      account_type = AccountType[form.account_type.data]
    except:
      flash('Invalid account type {}'.format(form.account_type.data), 'danger')
      return redirect(url_for('create_account'))
    user.set_account_type(account_type)
    db.session.add(user)
    db.session.commit()
    send_create_account_email(user, password)
    flash('Created user {} with password {}'.format(user.username, password), 'success')
    return redirect(url_for('index'))
  return render_template('create_account.html', title='Create Account', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = ResetPasswordRequestForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user:
      send_password_reset_email(user)
    flash('Check your email for the instructions to reset your password', 'info')
    return redirect(url_for('login'))
  return render_template('reset_password_request.html',
                         title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  user = User.verify_reset_password_token(token)
  if not user:
    return redirect(url_for('index'))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    user.set_password(form.password.data)
    db.session.commit()
    flash('Your password has been reset.', 'success')
    return redirect(url_for('login'))
  return render_template('reset_password.html', form=form)

@app.route('/hospital/<id>')
def hospital(id):
  hospital = Hospital.query.filter_by(id=id).first_or_404()
  return render_template('hospital.html', hospital=hospital)
