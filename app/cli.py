import click, os
from app import app, db
from app.models import User, AccountType

@app.cli.command('setup-debug-database')
def setup_debug_database():
  if app.debug:
    click.echo('Deleting all users and adding default user \'tim\'')
    User.query.delete()
    u = User(username='tim', email='tim@test.com', account_type=AccountType.admin)
    u.set_password('tim')
    db.session.add(u)
    db.session.commit()
  else:
    click.echo('This command only works in debug mode...')

@app.cli.command('open-mail-server')
def open_mail_server():
  os.system('python -m smtpd -n -c DebuggingServer localhost:8025')
