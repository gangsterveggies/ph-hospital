"""fix migrations

Revision ID: e48efb53cf05
Revises: 
Create Date: 2020-05-02 23:23:50.510399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e48efb53cf05'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('supply_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('info', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supply_type_name'), 'supply_type', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('account_type', sa.Enum('admin', 'donor', 'doctor', name='accounttype'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('hospital',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('location', sa.String(length=128), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=True),
    sa.Column('region', sa.String(length=128), nullable=True),
    sa.Column('contact', sa.String(length=128), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hospital_name'), 'hospital', ['name'], unique=True)
    op.create_table('request_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requester_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('single_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supply_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('show_donors', sa.Boolean(), nullable=True),
    sa.Column('donor_id', sa.Integer(), nullable=True),
    sa.Column('donation_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['donor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['request_group.id'], ),
    sa.ForeignKeyConstraint(['supply_id'], ['supply_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_single_request_donation_timestamp'), 'single_request', ['donation_timestamp'], unique=False)
    op.create_table('request_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status_type', sa.Enum('requested', 'looking', 'matched', 'sent', 'completed', name='requeststatustype'), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['single_request.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_request_status_timestamp'), 'request_status', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_request_status_timestamp'), table_name='request_status')
    op.drop_table('request_status')
    op.drop_index(op.f('ix_single_request_donation_timestamp'), table_name='single_request')
    op.drop_table('single_request')
    op.drop_table('request_group')
    op.drop_index(op.f('ix_hospital_name'), table_name='hospital')
    op.drop_table('hospital')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_supply_type_name'), table_name='supply_type')
    op.drop_table('supply_type')
    # ### end Alembic commands ###
