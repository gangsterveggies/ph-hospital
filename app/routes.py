from flask import render_template, flash, redirect, url_for, jsonify
from flask import request as flask_request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, CreateAccountForm, ResetPasswordRequestForm, ResetPasswordForm, HospitalEditOwnerForm, AddSupplyTypeForm, CreateHospitalForm, SupplyForm, RequestForm, ValidateAccountForm, SendSuppliesForm
from app.models import User, AccountType, Hospital, SupplyType, RequestGroup, SingleRequest, RequestStatus, RequestStatusType
from app.helpers import admin_required, doctor_required, donor_required
from app.email import send_password_reset_email, send_create_account_email
from werkzeug.urls import url_parse
from datetime import datetime

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
    next_page = flask_request.args.get('next')
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
    return redirect(url_for('profile'))
  return render_template('create_account.html', title='Create Account', form=form)

@app.route('/validate_account', methods=['GET', 'POST'])
@admin_required
def validate_account():
  form = ValidateAccountForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user.account_type == AccountType.doctor:
      hospital = Hospital.query.filter_by(name=form.hospital.data).first()
      if hospital is None:
        flash('Hospital not found', 'danger')
        return render_template('validate_account.html', title='Validate Account', form=form)
      user.hospital = hospital
    user.verified = True
    for requests in user.requests:
      for single_request in requests.item_list:
        single_request.show_donors=True
        request_status = RequestStatus(status_type=RequestStatusType.looking, single_request=single_request)
        db.session.add(request_status)
    db.session.commit()
    flash('Verified user successfully', 'success')
    return redirect(url_for('profile'))
  return render_template('validate_account.html', title='Validate Account', form=form)

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
## Request pages
#######################################

@app.route('/request', methods=['GET', 'POST'])
@doctor_required
def request():
  form = RequestForm()
  if form.validate_on_submit():
    request = RequestGroup(requester_id=current_user.id)
    db.session.add(request)
    for request_entry in form.supply_entries.data:
      single_request = SingleRequest(supply_id=request_entry['supply_type'], request=request, quantity=request_entry['quantity'], show_donors=False)
      db.session.add(single_request)
      request_status = RequestStatus(status_type=RequestStatusType.requested, single_request=single_request)
      db.session.add(request_status)
      if User.is_verified(current_user):
        single_request.show_donors=True
        request_status = RequestStatus(status_type=RequestStatusType.looking, single_request=single_request)
        db.session.add(request_status)
    db.session.commit()
    flash('Your PPE request was successfully processed', 'success')
    return redirect(url_for('profile'))
  return render_template('request.html', title='Request PPE', form=form)

#######################################
## Donor pages
#######################################

@app.route('/donation_log', methods=['GET'])
@donor_required
def donation_log():
  requests = []
  request_query = SingleRequest.query.filter_by(show_donors=True).order_by(SingleRequest.id.desc())
  for single_request in request_query:
    requests.append({'id': single_request.id
                     ,'requester': single_request.request.requester.username
                     ,'supply': single_request.supply.name
                     ,'quantity': single_request.quantity})
  return render_template('donation_log.html', title='List of requests', requests=requests)

@app.route('/match_donation/<id>', methods=['GET'])
@donor_required
def match_donation(id):
  single_request = SingleRequest.query.filter_by(id=id).first()
  if single_request is None:
    flash('Invalid request index', 'danger')
  else:
    if single_request.show_donors:
      request_status = RequestStatus(status_type=RequestStatusType.matched, single_request=single_request)
      db.session.add(request_status)
      single_request.show_donors = False
      single_request.donation_timestamp = datetime.utcnow()
      single_request.donor = current_user
      try:
        db.session.commit()
        flash('You were successfully matched to the request', 'success')
      except:
        db.session.rollback()
        flash('This request has been fulfilled by another donor', 'danger')
    else:
      flash('This request has been fulfilled by another donor', 'danger')
  return redirect(url_for('donation_log'))

# https://github.com/lepture/flask-wtf/issues/182
@app.route('/drop_donation/<id>', methods=['GET'])
@donor_required
def drop_donation(id):
  single_request = SingleRequest.query.filter_by(id=id).first()
  if single_request is None:
    flash('Invalid request index', 'danger')
  else:
    if single_request.donor == current_user:
      request_status = RequestStatus(status_type=RequestStatusType.looking, single_request=single_request)
      db.session.add(request_status)
      single_request.show_donors = True
      single_request.donor = None
      db.session.commit()
      flash('You dropped the PPE request', 'success')
    else:
      flash('You don\'t have access to this request', 'danger')
  return redirect(url_for('profile'))

@app.route('/send_donation/<id>', methods=['GET'])
@donor_required
def send_donation(id):
  single_request = SingleRequest.query.filter_by(id=id).first()
  if single_request is None:
    flash('Invalid request index', 'danger')
  else:
    if single_request.donor == current_user:
      request_status = RequestStatus(status_type=RequestStatusType.sent, single_request=single_request)
      db.session.add(request_status)
      db.session.commit()
      flash('You marked the request as sent', 'success')
    else:
      flash('You don\'t have access to this request', 'danger')
  return redirect(url_for('profile'))

#######################################
## Misc pages
#######################################

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
  donation_list = []
  donation_index = {}
  if User.is_donor(current_user):
    for single_request in current_user.donations.order_by(SingleRequest.donation_timestamp.desc()):
      if not single_request.completed:
        form = SendSuppliesForm(str(single_request.id), single_request.quantity - (single_request.fulfilled or 0))
        app.logger.info(single_request.quantity - (single_request.fulfilled or 0))
        donation_index[single_request.id] = form
        donation_list.append({'id': single_request.id
                            ,'requester': single_request.request.requester.username
                            ,'supply': single_request.supply.name
                            ,'quantity': single_request.quantity
                            ,'fulfilled': single_request.fulfilled
                            ,'completed': single_request.completed
                            ,'form': form})
      else:
        donation_list.append({'id': single_request.id
                            ,'requester': single_request.request.requester.username
                            ,'supply': single_request.supply.name
                            ,'quantity': single_request.quantity
                            ,'completed': single_request.completed})

  if flask_request.method == 'POST':    
    try:
      form_name = flask_request.form['form-name']
      form = donation_index[int(form_name)]
      if form.submit.data and form.validate_on_submit():
        single_request = SingleRequest.query.filter_by(id=form_name).first()
        single_request.fulfilled = int(form.quantity.data) + (single_request.fulfilled or 0)
        request_status = RequestStatus(status_type=RequestStatusType.sent, single_request=single_request, units=int(form.quantity.data))
        db.session.add(request_status)
        if single_request.fulfilled == single_request.quantity:
          single_request.completed = True
          request_status = RequestStatus(status_type=RequestStatusType.completed, single_request=single_request)
          db.session.add(request_status)
        db.session.commit()
        flash("You marked more {} units as sent".format(form.quantity.data), 'success')
        return redirect(url_for('profile'))
      else:
        flash('Number of units out of range', 'danger')
        return redirect(url_for('profile'))
    except:
      flash('Invalid operation', 'danger')
      return redirect(url_for('profile'))

  request_list = []
  if User.is_doctor(current_user):
    for request_group in current_user.requests.order_by(RequestGroup.id.desc()):
      request_list += [{'id': request_group.id
                        ,'requested_items': [{'supply': single_request.supply.name
                                              ,'quantity': single_request.quantity
                                              ,'status': [{'type': status.status_type.name
                                                           ,'timestamp': status.timestamp}
                                                          for status in single_request.status_list]}
                                             for single_request in request_group.item_list]}]
  return render_template('profile.html', title='Profile page', donations=donation_list, requests=request_list)
