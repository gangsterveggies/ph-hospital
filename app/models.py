from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login, app
from flask_login import UserMixin
import enum, random, string, jwt
from time import time
from datetime import datetime

class AccountType(enum.Enum):
  admin = 1
  donor = 2
  hospital = 3
  volunteer = 4

class OrderStatus(enum.Enum):
  pending = 1
  verified = 2
  received = 3

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  account_type = db.Column(db.Enum(AccountType))
  hospital = db.relationship('Hospital', uselist=False, backref='owner')
  donations = db.relationship('DonationGroup', backref='donor', lazy='dynamic')

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
  donations = db.relationship('Donation', backref='supply', lazy='dynamic')

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
  donations = db.relationship('DonationGroup', backref='hospital', lazy='dynamic')

  def __repr__(self):
    return '<Hospital {}>'.format(self.name)

class Donation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  supply_id = db.Column(db.Integer, db.ForeignKey('supply_type.id'))
  group_id =  db.Column(db.Integer, db.ForeignKey('donation_group.id'))
  quantity = db.Column(db.Integer)

  def __repr__(self):
    supply = SupplyType.query.filter_by(id=self.supply_id).first()
    return '<DonationSingle {}x{}>'.format(supply.name, self.quantity)
  
class DonationGroup(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  donor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
  donations = db.relationship('Donation', backref='group', lazy='dynamic')
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  order_status = db.Column(db.Enum(OrderStatus))

  def __repr__(self):
    return '<Donation {}>'.format(self.donations)
