"""Create m2m Strike self ref. table

Revision ID: b01ba6d159de
Revises: c0bf17dc4c7c
Create Date: 2023-06-19 14:21:55.067353

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = 'b01ba6d159de'
down_revision = 'c0bf17dc4c7c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('strike_to_itself_associations',
    sa.Column('strike_left_id', sa.BigInteger(), nullable=False),
    sa.Column('strike_right_id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['strike_left_id'], ['strikes.id'], name=op.f('fk_strike_to_itself_associations_strike_left_id_strikes'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['strike_right_id'], ['strikes.id'], name=op.f('fk_strike_to_itself_associations_strike_right_id_strikes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('strike_left_id', 'strike_right_id', name=op.f('pk_strike_to_itself_associations'))
    )
    op.add_column('strikes', sa.Column('union_in_charge_id', sa.BigInteger(), nullable=True))
    op.drop_constraint('fk_strikes_union_in_charge_unions', 'strikes', type_='foreignkey')
    op.create_foreign_key(op.f('fk_strikes_union_in_charge_id_unions'), 'strikes', 'unions', ['union_in_charge_id'], ['id'], ondelete='SET NULL')
    op.drop_column('strikes', 'union_in_charge')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strikes', sa.Column('union_in_charge', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_strikes_union_in_charge_id_unions'), 'strikes', type_='foreignkey')
    op.create_foreign_key('fk_strikes_union_in_charge_unions', 'strikes', 'unions', ['union_in_charge'], ['id'], ondelete='SET NULL')
    op.drop_column('strikes', 'union_in_charge_id')
    op.drop_table('strike_to_itself_associations')
    # ### end Alembic commands ###
