import click, os, random
from faker import Faker
from app import app, db
from app.models import User, AccountType, Hospital, SupplyType, RequestStatus, SingleRequest, RequestGroup, RequestStatusType, Pledge

supply_list_pairs = [
  ("N95 Mask", "https://en.wikipedia.org/wiki/N95_mask"),
  ("Surgical Mask", "https://en.wikipedia.org/wiki/Surgical_mask"),
  ("Disposable Foot Cover", ""),
  ("Reusable Foot Cover", ""),
  ("Reusable Bunny Suit", ""),
  ("Goggles", ""),
  ("Food Packs", ""),
  ("Tent", ""),
  ("Mattress", "")
]

@app.cli.command('setup-debug-database')
def setup_debug_database():
#  if app.debug:
  click.echo('Deleting all donations and request')
  RequestStatus.query.delete()
  SingleRequest.query.delete()
  RequestGroup.query.delete()
  Pledge.query.delete()
  Hospital.query.delete()
  SupplyType.query.delete()
  db.session.commit()

  for s_name, s_info in supply_list_pairs:
    supply = SupplyType.query.filter_by(name=s_name).first()
    if supply is None:
      supply = SupplyType(name=s_name, info=s_info)
      db.session.add(supply)
  db.session.commit()
  
  click.echo('Deleting all users and adding default users')
  
  user_list = User.query.all()
  for u in user_list:
    u.verified = []
  db.session.commit()
    
  User.query.delete()
  user_tim = User(username='tim', email='tim@test.com', account_type=AccountType.admin)
  user_tim.verified_tag = True
  user_tim.set_password('tim')
  db.session.add(user_tim)

  for i in range(5):
    u = User(username='donor' + str(i + 1), email='donor' + str(i + 1) + '@test.com', account_type=AccountType.donor, verified_tag=True)
    u.set_password('donor')
    db.session.add(u)
    
  db.session.commit()

  click.echo('Deleting all hospitals and adding default ones')

  fake = Faker()
  f = lambda x : str(x[0]) + " " + str(x[1])
  hospital_list = []
  for i in range(10):
    h = Hospital(name=(fake.city() + " Hospital"), location=f(fake.local_latlng()), address=fake.address(), contact=fake.phone_number())
    hospital_list.append(h)
    db.session.add(h)
  db.session.commit()
    
  for i in range(5):
    u = User(username='doctor' + str(i + 1), email='doctor' + str(i + 1) + '@test.com', account_type=AccountType.doctor, hospital=random.choice(hospital_list))
    u.set_password('doctor')
    db.session.add(u)

    for _a in range(3):
      request = RequestGroup(requester=u)
      db.session.add(request)
      for _ in range(4):
        single_request = SingleRequest(supply_id=random.choice(range(1,len(supply_list_pairs))), request=request, quantity=10, custom_info=fake.paragraph(), show_donors=False)
        db.session.add(single_request)
        request_status = RequestStatus(status_type=RequestStatusType.requested, single_request=single_request)
        db.session.add(request_status)

  db.session.commit()
#  else:
#    click.echo('This command only works in debug mode...')

@app.cli.command('open-mail-server')
def open_mail_server():
  os.system('python -m smtpd -n -c DebuggingServer localhost:8025')
