"""Add fk to Union from Strike

Revision ID: c0bf17dc4c7c
Revises: 587df00fefd9
Create Date: 2023-06-19 13:40:19.685465

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = 'c0bf17dc4c7c'
down_revision = '587df00fefd9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('strikes', sa.Column('union_in_charge', sa.BigInteger(), nullable=True))
    op.create_foreign_key(op.f('fk_strikes_union_in_charge_unions'), 'strikes', 'unions', ['union_in_charge'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_strikes_union_in_charge_unions'), 'strikes', type_='foreignkey')
    op.drop_column('strikes', 'union_in_charge')

    # ### end Alembic commands ###
