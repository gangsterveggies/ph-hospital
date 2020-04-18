import click, os
from faker import Faker
from app import app, db
from app.models import User, AccountType, Hospital, SupplyType

@app.cli.command('setup-debug-database')
def setup_debug_database():
  if app.debug:
    click.echo('Deleting all users and adding default users')
    User.query.delete()
    u = User(username='tim', email='tim@test.com', account_type=AccountType.admin)
    u.set_password('tim')
    db.session.add(u)

    for i in range(5):
      u = User(username='donor' + str(i + 1), email='donor' + str(i + 1) + '@test.com', account_type=AccountType.donor)
      u.set_password('donor')
      db.session.add(u)

    for i in range(5):
      u = User(username='hospital' + str(i + 1), email='hospital' + str(i + 1) + '@test.com', account_type=AccountType.hospital)
      u.set_password('hospital')
      db.session.add(u)

    for i in range(5):
      u = User(username='volunteer' + str(i + 1), email='volunteer' + str(i + 1) + '@test.com', account_type=AccountType.volunteer)
      u.set_password('volunteer')
      db.session.add(u)
    
    db.session.commit()

    click.echo('Deleting all hospitals and adding default ones')
    Hospital.query.delete()

    fake = Faker()
    f = lambda x : str(x[0]) + " " + str(x[1])
    for i in range(10):
      h = Hospital(name=fake.company(), location=f(fake.local_latlng()), address=fake.address(), contact=fake.phone_number())
      db.session.add(h)
    db.session.commit()
  else:
    click.echo('This command only works in debug mode...')

@app.cli.command('add-base-ppes')
def add_base_ppes():
  if app.debug:
    click.echo('Deleting all current PPEs')
    SupplyType.query.delete()
  supply_list_pairs = [
    ("N95 Regular", "https://en.wikipedia.org/wiki/N95_mask"),
    ("N95 Small", "https://en.wikipedia.org/wiki/N95_mask"),
    ("Surgical Mask", "https://en.wikipedia.org/wiki/Surgical_mask"),
    ("Gloves", "https://en.wikipedia.org/wiki/Medical_glove"),
    ("Face Shields", "https://en.wikipedia.org/wiki/Face_shield#Medical"),
    ("Body Suits", ""),
    ("Wipes", ""),
    ("Sanitizer", ""),
    ("Googles", ""),
    ("Gowns", "")
  ]
  for s_name, s_info in supply_list_pairs:
    supply = SupplyType.query.filter_by(name=s_name).first()
    if supply is None:
      supply = SupplyType(name=s_name, info=s_info)
      db.session.add(supply)
  db.session.commit()

@app.cli.command('open-mail-server')
def open_mail_server():
  os.system('python -m smtpd -n -c DebuggingServer localhost:8025')
