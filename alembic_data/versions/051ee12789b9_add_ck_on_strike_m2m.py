"""add ck on strike m2m

Revision ID: 051ee12789b9
Revises: 3f2bf264a901
Create Date: 2023-07-14 12:28:53.894534

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

from internal.database import Base

# revision identifiers, used by Alembic.
revision = '051ee12789b9'
down_revision = '3f2bf264a901'
branch_labels = None
depends_on = None

table_name = 'strike_to_itself_associations'
constraint_name = 'left_ne_right'
constraint_full_name = Base.metadata.naming_convention['ck'] % \
                       {'constraint_name': constraint_name, 'table_name': table_name}


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name,
        table_name,
        r'strike_left_id != strike_right_id'
    )


def downgrade() -> None:
    op.drop_constraint(constraint_full_name, table_name)
