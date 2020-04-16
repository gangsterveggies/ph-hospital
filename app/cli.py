import click, os
from app import app, db
from app.models import User, AccountType, Hospital

@app.cli.command('setup-debug-database')
def setup_debug_database():
  if app.debug:
    click.echo('Deleting all users and adding default user \'tim\'')
    User.query.delete()
    u = User(username='tim', email='tim@test.com', account_type=AccountType.admin)
    u.set_password('tim')
    db.session.add(u)
    db.session.commit()

    click.echo('Deleting all hospitals and adding default ones')
    Hospital.query.delete()
    for i in range(10):
      h = Hospital(name="UPMC" + str(i + 1), location="41.407845, -75.655145", address="200 Lothrop Street Pittsburgh, PA 15213 ", contact="4120000000")
      db.session.add(h)
    db.session.commit()
  else:
    click.echo('This command only works in debug mode...')

@app.cli.command('open-mail-server')
def open_mail_server():
  os.system('python -m smtpd -n -c DebuggingServer localhost:8025')
