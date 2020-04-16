"""add supply type and hospital

Revision ID: 59496d216729
Revises: 216c1731d078
Create Date: 2020-04-16 01:27:58.780273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59496d216729'
down_revision = '216c1731d078'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('supply_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supply_type_name'), 'supply_type', ['name'], unique=True)
    op.create_table('hospital',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('location', sa.String(length=128), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=True),
    sa.Column('contact', sa.String(length=128), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hospital_name'), 'hospital', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hospital_name'), table_name='hospital')
    op.drop_table('hospital')
    op.drop_index(op.f('ix_supply_type_name'), table_name='supply_type')
    op.drop_table('supply_type')
    # ### end Alembic commands ###