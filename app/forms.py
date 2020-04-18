from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, SupplyType

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Sign In')

class CreateAccountForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  account_type = RadioField('Account Type', choices=[('admin', 'Admin'), ('donor', 'Donor'), ('hospital', 'Hospital'), ('volunteer', 'Volunteer')], validators=[DataRequired()])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
    'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Request Password Reset')

class HospitalEditOwnerForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  submit = SubmitField('Change Owner')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is None:
      raise ValidationError('Username not found.')

class AddSupplyTypeForm(FlaskForm):
  name = StringField('PPE type', validators=[DataRequired()])
  info = StringField('Info url')
  submit = SubmitField('Add PPE type')

  def validate_name(self, name):
    supply = SupplyType.query.filter_by(name=name.data).first()
    if not supply is None:
      raise ValidationError('There already is a PPE named {}.'.format(name.data))
