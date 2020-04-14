from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login, app
from flask_login import UserMixin
import enum, random, string, jwt
from time import time

class AccountType(enum.Enum):
  admin = 1
  donor = 2
  hospital = 3
  volunteer = 4

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  account_type = db.Column(db.Enum(AccountType))

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

  def is_admin(self):
    return self.is_authenticated and self.account_type == AccountType.admin

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
