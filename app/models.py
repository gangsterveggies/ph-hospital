from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
import enum, random, string

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
