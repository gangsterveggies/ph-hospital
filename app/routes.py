from flask import render_template, flash, redirect, url_for, jsonify
from flask import request as flask_request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, CreateAccountForm, ResetPasswordRequestForm, ResetPasswordForm, HospitalEditOwnerForm, AddSupplyTypeForm, CreateHospitalForm, SupplyForm, RequestForm, VerifyAccountForm, SendSuppliesForm, UserFilterForm, SupplyFilterForm
from app.models import User, AccountType, Hospital, SupplyType, RequestGroup, SingleRequest, RequestStatus, RequestStatusType, Pledge
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
      next_page = url_for('profile')
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
  for subform in form.supply_entries:
    subform.supply_type.choices = [(s.id, s.name) for s in SupplyType.query.order_by('name')]
  if form.validate_on_submit():
    request = RequestGroup(requester_id=current_user.id)
    db.session.add(request)
    for request_entry in form.supply_entries.data:
      single_request = SingleRequest(supply_id=request_entry['supply_type'], request=request, quantity=request_entry['quantity'], custom_info=request_entry['custom_info'], show_donors=False)
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

@app.route('/donation_log', methods=['GET', 'POST'])
@donor_required
def donation_log():
  form1 = UserFilterForm(prefix='f1')
  form2 = SupplyFilterForm(prefix='f2')
  form2.supply_type.choices = [(s.id, s.name) for s in SupplyType.query.order_by('name')]
  
  user_filters = flask_request.args.get('user', default=None, type=str)
  if user_filters is None  or user_filters == '':
    user_filters = []
  else:
    user_filters = [fl.strip() for fl in user_filters.split('$')]
  user_filters = list(set(user_filters))

  supply_filters = flask_request.args.get('supply', default=None, type=str)
  if supply_filters is None or supply_filters == '':
    supply_filters = []
  else:
    supply_filters = [fl.strip() for fl in supply_filters.split('$')]
  supply_filters = list(set(supply_filters))

  sort_status = (flask_request.args.get('sortby', default=None, type=str)
                 ,flask_request.args.get('sorttype', default=None, type=str))
  if sort_status[0] is None:
    sort_status = ("0", sort_status[1])
  if sort_status[1] is None:
    sort_status = (sort_status[0], "0")

  supply_filters_names = []
  for supply in supply_filters:
    supply_obj = SupplyType.query.filter_by(id = supply).first()
    if supply_obj is None:
      flash("Invalid filter", "danger")
      return render_template('donation_log.html', title='List of requests', requests=[], user_filters=[], supply_filters=[], form1=form1, form2=form2)
    supply_filters_names.append({'id': supply, 'name': supply_obj.name})

  if form1.submit.data and form1.validate_on_submit():
    user_filters.append(form1.username.data)
    return redirect(url_for('donation_log', user='$'.join(user_filters), supply='$'.join(map(str, supply_filters)), sortby=sort_status[0], sorttype=sort_status[1]))

  if form2.submit.data and form2.validate_on_submit():
    supply_filters.append(form2.supply_type.data)
    return redirect(url_for('donation_log', user='$'.join(user_filters), supply='$'.join(map(str, supply_filters)), sortby=sort_status[0], sorttype=sort_status[1]))

  requests = []
  base_request_query = db.session.query(SingleRequest, SupplyType, User).filter_by(show_donors=True).join(
      RequestGroup, SingleRequest.group_id == RequestGroup.id).join(
        User, RequestGroup.requester_id == User.id).join(
          SupplyType, SingleRequest.supply_id == SupplyType.id)

  user_query = None
  for user in user_filters:
    local_query = base_request_query.filter(
          User.username == user)
    if user_query is None:
      user_query = local_query
    else:
      user_query = user_query.union(local_query)

  supply_query = None
  for supply in supply_filters:
    local_query = base_request_query.filter(SupplyType.id == supply)
    if supply_query is None:
      supply_query = local_query
    else:
      supply_query = supply_query.union(local_query)

  filter_list = [user_query, supply_query]
  request_query = None
  for filter_unit in filter_list:
    if filter_unit is not None:
      if request_query is None:
        request_query = filter_unit
      else:
#        request_query = request_query.intersect(filter_unit)
        subquery = filter_unit.subquery()
        subquery_field = None
        if 'id' in dir(subquery.c):
          subquery_field = subquery.c.id
        else:
          single_request_id_field = None
          for field in dir(subquery.c):
            if field.endswith("single_request_id"):
              single_request_id_field = field
              break
          if single_request_id_field is not None:
            subquery_field = getattr(subquery.c, single_request_id_field)
        if subquery_field is not None:
          request_query = request_query.join(subquery, SingleRequest.id == subquery_field)

  if request_query is None:
    request_query = base_request_query
  if sort_status == ("0", "0"):
    sort_query = SingleRequest.id.desc()
  elif sort_status == ("0", "1"):
    sort_query = SingleRequest.id.asc()
  elif sort_status == ("1", "0"):
    sort_query = User.username.desc()
  elif sort_status == ("1", "1"):
    sort_query = User.username.asc()
  elif sort_status == ("2", "0"):
    sort_query = SingleRequest.quantity.desc()
  elif sort_status == ("2", "1"):
    sort_query = SingleRequest.quantity.asc()
  elif sort_status == ("3", "0"):
    sort_query = SupplyType.name.desc()
  elif sort_status == ("3", "1"):
    sort_query = SupplyType.name.asc()
  request_query = request_query.order_by(sort_query)
  request_query = request_query.all()

  for (single_request, supply, user) in request_query:
    requests.append({'id': single_request.id
                     ,'requester': user.username
                     ,'supply': supply.name
                     ,'quantity': single_request.quantity
                     ,'fulfilled': single_request.fulfilled
                     ,'request_timestamp': single_request.request_timestamp})
  return render_template('donation_log.html', title='List of requests', requests=requests, user_filters=user_filters, supply_filters=supply_filters_names, form1=form1, form2=form2, sort_status=sort_status)

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
  return redirect(url_for('profile'))

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

@app.route('/pledge_donation', methods=['POST'])
@donor_required
def pledge_donation():
  single_request = SingleRequest.query.filter_by(id=int(flask_request.form['id'])).first()
  quantity = int(flask_request.form['quantity'])
  if single_request is None:
    return jsonify({'success': False})
  
  if single_request.quantity - single_request.fulfilled < quantity:
    return jsonify({'success': False})

  pledge = Pledge(quantity=quantity, single_request=single_request, pledger=current_user)
  db.session.add(pledge)
  db.session.commit()
  
  return jsonify({'success': True})

@app.route('/confirm_pledge', methods=['POST'])
@donor_required
def confirm_pledge():
  pledge = Pledge.query.filter_by(id=int(flask_request.form['id'])).first()
  if pledge is None or pledge.pledger != current_user:
    return jsonify({'success': False})
  
  pledge.confirm()
  db.session.commit()
  
  return jsonify({'success': True})

#######################################
## User pages
#######################################

@app.route('/user/<username>', methods=['GET', 'POST'])
@donor_required
def user_page(username):
  user = User.query.filter_by(username=username).first_or_404()
  verifications = user.verified.limit(3).all()
  self_verified = user.is_verified_by(current_user)
  if user.username == current_user.username:
    return redirect(url_for('profile'))
  if user.account_type == AccountType.doctor and not self_verified:
    form = VerifyAccountForm()
    if form.validate_on_submit():
      user.verified_tag = True
      current_user.verify(user)
      for requests in user.requests:
        for single_request in requests.item_list:
          single_request.show_donors=True
          request_status = RequestStatus(status_type=RequestStatusType.looking, single_request=single_request)
          db.session.add(request_status)
      db.session.commit()
      flash('Verified {} successfully'.format(username), 'success')
      return redirect(url_for('user_page', username=username))
    else:
      return render_template('user.html', title='User {}'.format(username), user=user, form=form, verifications=verifications, self_verified=self_verified)
  else:
    return render_template('user.html', title='User {}'.format(username), user=user, verifications=verifications, self_verified=self_verified)

@app.route('/user/<username>/popup')
@donor_required
def user_popup(username):
  user = User.query.filter_by(username=username).first_or_404()
  verifications = user.verified.limit(3).all()
  self_verified = user.is_verified_by(current_user)
  user_verified = user.verified_tag
  return render_template('user_popup.html', user=user, verifications=verifications, self_verified=self_verified, user_verified=user_verified)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
  pledge_list = []
  if User.is_donor(current_user):
    for pledge in current_user.pledges.order_by(Pledge.timestamp.desc()):
      pledge_list.append({'id': pledge.id
                          ,'requester': pledge.single_request.request.requester.username
                          ,'supply': pledge.single_request.supply.name
                          ,'quantity': pledge.quantity
                          ,'request_quantity': pledge.single_request.quantity
                          ,'timestamp': pledge.timestamp
                          ,'custom_info': pledge.single_request.custom_info
                          ,'completed': pledge.confirmed})

  request_list = []
  if User.is_doctor(current_user):
    for request_group in current_user.requests.order_by(RequestGroup.id.desc()):
      request_list += [{'id': request_group.id
                        ,'requested_items': [{'supply': single_request.supply.name
                                              ,'fulfilled': single_request.fulfilled
                                              ,'quantity': single_request.quantity
                                              ,'completed': single_request.completed
                                              ,'custom_info': single_request.custom_info
                                              ,'donor': single_request.donor
                                              ,'status': [{'type': status.status_type.name
                                                           ,'quantity': status.units
                                                           ,'timestamp': status.timestamp}
                                                          for status in single_request.status_list]}
                                             for single_request in request_group.item_list]}]

  verifications = current_user.verified.limit(3).all()

  return render_template('profile.html', title='Profile page', pledges=pledge_list, requests=request_list, verifications=verifications)

@app.route('/verify_list', methods=['GET', 'POST'])
@donor_required
def verify_list():
  user_list = []
  user_index = {}
  users = User.query.filter_by(verified_tag=False)

  for user in users:
    form = VerifyAccountForm(prefix=str(user.id))
    user_list.append({'username': user.username
                      ,'id': user.id
                      ,'form': form})
    user_index[str(user.id)] = (form, user)

  if flask_request.method == 'POST':    
    try:
      form_name = flask_request.form['form-name']
      form, user = user_index[form_name]
      if form.submit.data:
        user.verified_tag = True
        current_user.verify(user)
        for requests in user.requests:
          for single_request in requests.item_list:
            single_request.show_donors=True
            request_status = RequestStatus(status_type=RequestStatusType.looking, single_request=single_request)
            db.session.add(request_status)
        db.session.commit()
        flash('Verified {} successfully'.format(user.username), 'success')
        return redirect(url_for('verify_list'))
    except Exception as e:
      app.logger.info(e)
      return redirect(url_for('verify_list'))

  return render_template('verify_list.html', title='Users to verify', users=user_list)
