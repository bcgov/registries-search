"""index-by-idp-guid

Revision ID: 3faf50891480
Revises: f7d39c77458f
Create Date: 2022-12-13 11:30:36.659379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3faf50891480'
down_revision = 'f7d39c77458f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_user_idp_userid'), 'users', ['idp_userid'], unique=True)
    op.create_unique_constraint('users_idp_userid_key', 'users', ['idp_userid'])


def downgrade():
    op.drop_index(op.f('ix_user_idp_userid'), table_name='users')
    op.drop_constraint('users_idp_userid_key', 'users', type_='unique')