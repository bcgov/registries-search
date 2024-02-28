"""empty message

Revision ID: b7678d3f3b25
Revises: f01f4a22bb30
Create Date: 2024-02-27 11:31:40.194245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b7678d3f3b25'
down_revision = 'f01f4a22bb30'
branch_labels = None
depends_on = None

new_enum_name = 'UPDATE_EXT'


def upgrade():
    op.execute(f"ALTER TYPE solrdoceventtype ADD VALUE '{new_enum_name}'")


def downgrade():
    op.execute(f"""
               DELETE
               FROM pg_enum
               WHERE enumlabel='{new_enum_name}'
                AND enumtypid = (SELECT oid
                                 FROM pg_type
                                 WHERE typname='solrdoceventtype')
               """)
