"""empty message

Revision ID: c8ee6bee0f3d
Revises: b7678d3f3b25
Create Date: 2024-02-29 14:37:15.466894

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c8ee6bee0f3d'
down_revision = 'b7678d3f3b25'
branch_labels = None
depends_on = None

new_enum_name = 'UPDATE_CEASE'


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
