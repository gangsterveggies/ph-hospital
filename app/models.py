from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login, app
from flask_login import UserMixin
import enum, random, string, jwt
from time import time
from datetime import datetime

class AccountType(enum.Enum):
  admin = 1
  donor = 2
  doctor = 3

class RequestStatusType(enum.Enum):
  requested = 1 # PPE Requested
  looking = 2   # Looking for Donors
  matched = 3   # Donor matched
  sent = 4      # Item on the way
  completed = 5 # Order completed

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  account_type = db.Column(db.Enum(AccountType))
  verified = db.Column(db.Boolean, default=False)
  hospital = db.relationship('Hospital', uselist=False, backref='owner')
  requests = db.relationship('RequestGroup', backref='requester', lazy='dynamic')
  donations = db.relationship('SingleRequest', backref='donor', lazy='dynamic')

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def set_account_type(self, account_type):
    self.account_type = account_type

  def get_reset_password_token(self, expires_in=600):
    return jwt.encode(
      {'reset_password': self.id, 'exp': time() + expires_in},
      app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  @staticmethod
  def is_admin(u):
    return u.is_authenticated and u.account_type == AccountType.admin

  @staticmethod
  def is_doctor(u):
    return u.is_authenticated and (
      u.account_type == AccountType.admin or
      u.account_type == AccountType.doctor)

  @staticmethod
  def is_donor(u):
    return u.is_authenticated and (
      u.account_type == AccountType.admin or
      u.account_type == AccountType.donor) and u.verified

  @staticmethod
  def is_verified(u):
    return u.is_authenticated and u.verified
  
  @staticmethod
  def verify_reset_password_token(token):
    try:
      id = jwt.decode(token, app.config['SECRET_KEY'],
                      algorithms=['HS256'])['reset_password']
    except:
      return
    return User.query.get(id)
    
  @staticmethod
  def random_password():
    stringLength = 8
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

  def __repr__(self):
    return '<User {}>'.format(self.username)    

@login.user_loader
def load_user(id):
  return User.query.get(int(id))

class SupplyType(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=True, unique=True)
  info = db.Column(db.String(128))
  requests = db.relationship('SingleRequest', backref='supply', lazy='dynamic')

  def __repr__(self):
    return '<SupplyType {}>'.format(self.name)

class Hospital(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), index=True, unique=True)
  location = db.Column(db.String(128))
  address = db.Column(db.String(128))
  region = db.Column(db.String(128))
  contact = db.Column(db.String(128))
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

  def __repr__(self):
    return '<Hospital {}>'.format(self.name)

class RequestStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  status_type = db.Column(db.Enum(RequestStatusType))
  units = db.Column(db.Integer)
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  request_id = db.Column(db.Integer, db.ForeignKey('single_request.id'))

class SingleRequest(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  supply_id = db.Column(db.Integer, db.ForeignKey('supply_type.id'))
  group_id = db.Column(db.Integer, db.ForeignKey('request_group.id'))
  quantity = db.Column(db.Integer)
  fulfilled = db.Column(db.Integer)
  completed = db.Column(db.Boolean, default=False)
  show_donors = db.Column(db.Boolean)
  donor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  donation_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  current_status = db.Column(db.Enum(RequestStatusType))
  status_list = db.relationship('RequestStatus', backref='single_request', lazy='dynamic')

  def __repr__(self):
    supply = SupplyType.query.filter_by(id=self.supply_id).first()
    return '<RequestSingle {}x{}>'.format(supply.name, self.quantity)

class RequestGroup(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  item_list = db.relationship('SingleRequest', backref='request', lazy='dynamic')

  def __repr__(self):
    return '<Request {}>'.format(self.item_list.all())
