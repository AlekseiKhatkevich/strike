"""Add exc. constr. into Strike

Revision ID: 64244710c802
Revises: 30ed81dd1fee
Create Date: 2023-06-18 11:47:06.290429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64244710c802'
down_revision = '30ed81dd1fee'
branch_labels = None
depends_on = None

constraint_name = "duration_enterprise_exc_constraint"

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_exclude_constraint(
        constraint_name,
        "strikes",
        ("duration", "&&"),
        ("enterprise_id", "="),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_exclude_constraint(constraint_name, 'strikes')
    # ### end Alembic commands ###