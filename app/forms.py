from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, SubmitField, RadioField, SelectField, IntegerField, FormField, FieldList, BooleanField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length
from app.models import User, AccountType, SupplyType, Hospital

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Sign In')

class CreateAccountForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  account_type = RadioField('Account Type', choices=[('admin', 'Admin'), ('donor', 'Donor'), ('doctor', 'Doctor')], validators=[DataRequired()])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')

class VerifyAccountForm(FlaskForm):
  submit = SubmitField('Verify User')

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
  name = StringField('Item type', validators=[DataRequired()])
  info = StringField('Info url')
  submit = SubmitField('Add Item type')

  def validate_name(self, name):
    supply = SupplyType.query.filter_by(name=name.data).first()
    if not supply is None:
      raise ValidationError('There already is a Item named {}.'.format(name.data))

class CreateHospitalForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  location = StringField('Geographic location (coordinates)')
  address = StringField('Address', validators=[DataRequired()])
  region = StringField('Region')
  contact = StringField('Phone contact')
  owner = StringField('Username owner')
  submit = SubmitField('Change Hospital')

  def validate_owner(self, owner):
    if len(owner.data) != 0:
      user = User.query.filter_by(username=owner.data).first()
      if user is None:
        raise ValidationError('Owner username not found.')

  def validate_name(self, name):
    hospital = Hospital.query.filter_by(name=name.data).first()
    if not hospital is None:
      raise ValidationError('There already is a hospital with that name.')

class SupplyEntryForm(Form):
  supply_type = SelectField('Item Type', coerce=int)
  quantity = IntegerField('Quantity', [DataRequired(), NumberRange(min=1)])
  custom_info = TextAreaField('Customization', [Length(max=500)])

  def validate_supply_type(self, supply_type):
    supply = SupplyType.query.filter_by(id=supply_type.data).first()
    if supply is None:
      raise ValidationError('Invalid Item type.')

class SupplyForm(FlaskForm):
  name = StringField('Hospital Name', validators=[DataRequired()])
  supply_entries = FieldList(FormField(SupplyEntryForm), min_entries=1, max_entries=10)
  submit = SubmitField('Donate')

  def validate_name(self, name):
    hospital = Hospital.query.filter_by(name=name.data).first()
    if hospital is None:
      raise ValidationError('Hospital not found.')

class RequestForm(FlaskForm):
  supply_entries = FieldList(FormField(SupplyEntryForm), min_entries=1, max_entries=10)
  submit = SubmitField('Request Items')

class DonateSingleForm(FlaskForm):
  submit = SubmitField('Donate')

def SendSuppliesForm(prefix, maxRange):
  class TempForm(FlaskForm):
    submit = SubmitField('Send Units')
  setattr(TempForm, 'quantity', IntegerField('Quantity (at most {})'.format(maxRange), validators=[DataRequired(), NumberRange(min=1, max=maxRange)]))
  return TempForm(prefix=prefix)

class UserFilterForm(FlaskForm):
  username = StringField('Doctor username')
  submit = SubmitField('Add User Filter')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is None or user.account_type != AccountType.doctor:
      raise ValidationError('Invalid user.')

class SupplyFilterForm(FlaskForm):
  supply_type = SelectField('Item Type', coerce=int)
  submit = SubmitField('Add Item Filter')

  def validate_supply_type(self, supply_type):
    supply = SupplyType.query.filter_by(id=supply_type.data).first()
    if supply is None:
      raise ValidationError('Invalid Item type.')
