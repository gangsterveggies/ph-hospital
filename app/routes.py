from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, CreateAccountForm, ResetPasswordRequestForm, ResetPasswordForm, HospitalEditOwnerForm, AddSupplyTypeForm, CreateHospitalForm, DonateForm, SupplyForm
from app.models import User, AccountType, Hospital, SupplyType, DonationGroup, Donation, OrderStatus
from app.helpers import admin_required
from app.email import send_password_reset_email, send_create_account_email
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='Home')

#######################################
## Authentication pages
#######################################

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

#######################################
## Hospital related pages
#######################################

@app.route('/hospital')
def hospital():
  hospitals = Hospital.query.order_by(Hospital.name.asc()).all()
  return render_template('hospital.html', title='List of Hospitals', hospitals=hospitals)

@app.route('/hospital_view/<id>')
def hospital_view(id):
  hospital = Hospital.query.filter_by(id=id).first_or_404()
  owner = User.query.filter_by(id=hospital.owner_id).first().username if not hospital.owner_id is None else None
  return render_template('hospital_view.html', hospital=hospital, owner=owner)

@app.route('/hospital_edit_owner/<id>', methods=['GET', 'POST'])
@admin_required
def hospital_edit_owner(id):
  hospital = Hospital.query.filter_by(id=id).first_or_404()
  owner = hospital.owner.username if not hospital.owner is None else None
  form = HospitalEditOwnerForm(username=owner)
  if form.validate_on_submit():
    app.logger.info(form.username.data)
    user = User.query.filter_by(username=form.username.data).first()
    if user is None:
      flash('Invalid username', 'danger')
      return redirect(url_for('hospital_edit_owner'))
    if user.account_type == AccountType.donor:
      flash('User can\'t be a donor account', 'danger')
      return redirect(url_for('hospital_edit_owner', id=id))
    hospital.owner_id = user.id
    db.session.commit()
    flash('Hospital owner successfully altered', 'success')
    return redirect(url_for('hospital', id=id))
  return render_template('hospital_edit_owner.html', id=id, hospital=hospital, form=form, owner=owner)

@app.route('/create_hospital', methods=['GET', 'POST'])
@admin_required
def create_hospital():
  form = CreateHospitalForm()
  if form.validate_on_submit():
    owner_id = User.query.filter_by(username=form.owner.data).first().id if len(form.owner.data) != 0 else None
    hospital = Hospital(name=form.name.data, location=form.location.data
                        ,address=form.address.data, region=form.region.data
                        ,contact=form.contact.data, owner_id=owner_id)
    db.session.add(hospital)
    db.session.commit()
    flash('Added Hospital {}'.format(hospital.name), 'success')
    return redirect(url_for('hospital'))
  return render_template('create_hospital.html', title='Create Hospital', form=form)


#######################################
## Supply type related pages
#######################################

@app.route('/supply_type')
def supply_type():
  supplies = SupplyType.query.order_by(SupplyType.name.asc()).all()
  return render_template('supply_type.html', title='List of PPEs', supplies=supplies)

@app.route('/add_supply_type', methods=['GET', 'POST'])
@admin_required
def add_supply_type():
  form = AddSupplyTypeForm()
  if form.validate_on_submit():
    supply = SupplyType(name=form.name.data, info=form.info.data)
    db.session.add(supply)
    db.session.commit()
    flash('Added PPE type {}'.format(supply.name), 'success')
    return redirect(url_for('supply_type'))
  return render_template('add_supply_type.html', title='Add PPE', form=form)

#######################################
## Donation related pages
#######################################
@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
  form = SupplyForm()
  if form.validate_on_submit():
    hospital = Hospital.query.filter_by(name=form.name.data).first()
    donation = DonationGroup(donor_id=current_user.id, hospital_id=hospital.id, order_status=OrderStatus.pending)
    db.session.add(donation)
    for donation_entry in form.supply_entries.data:
      app.logger.info(donation_entry)
      single_donation = Donation(supply_id=donation_entry['supply_type'], group=donation, quantity=donation_entry['quantity'])
      db.session.add(single_donation)
    db.session.commit()
    flash('Thank you for your donation!', 'success')
    return redirect(url_for('index'))
  return render_template('donate.html', title='Donate PPE', form=form)

@app.route('/profile')
@login_required
def profile():
  donations = []
  if not current_user.is_anonymous:
    donation_list = []
    for donation_group in current_user.donations.order_by(DonationGroup.timestamp.desc()):
      app.logger.info(donation_group.order_status)
      donation_list += [{'id': donation_group.id
                         ,'hospital': donation_group.hospital.name
                         ,'hospital_id': donation_group.hospital.id
                         ,'timestamp': donation_group.timestamp
                         ,'order_status': donation_group.order_status
                         ,'donations': [{'supply': donation.supply.name
                                        ,'quantity': donation.quantity}
                                       for donation in donation_group.donations]}]
  return render_template('profile.html', title='Profile page', donations=donation_list)

@app.route('/verify_donation', methods=['POST'])
@admin_required
def verify_donation():
  donation = DonationGroup.query.filter_by(id=int(request.form['id'])).first()
  if donation is None:
    return jsonify({'success': False})
  app.logger.info(donation)
  donation.order_status = OrderStatus.verified
  db.session.commit()
  return jsonify({'success': True})
