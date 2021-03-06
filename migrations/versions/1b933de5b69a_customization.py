"""customization

Revision ID: 1b933de5b69a
Revises: a9b02ffedfb7
Create Date: 2020-05-10 01:40:14.015591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b933de5b69a'
down_revision = 'a9b02ffedfb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('single_request', sa.Column('custom_info', sa.String(length=505), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('single_request', 'custom_info')
    # ### end Alembic commands ###
