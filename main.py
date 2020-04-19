from app import app, db, cli
from app.models import User, AccountType, SupplyType, Hospital, DonationGroup

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'AccountType': AccountType, 'SupplyType': SupplyType, 'Hospital': Hospital, 'DonationGroup': DonationGroup}
