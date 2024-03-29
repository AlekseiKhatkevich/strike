"""Add user-strike m2m

Revision ID: dccae2fd7063
Revises: 476dbaa0c8c3
Create Date: 2023-06-15 16:32:34.775526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dccae2fd7063'
down_revision = '476dbaa0c8c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('strike_to_user_associations',
    sa.Column('strike_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['strike_id'], ['strikes.id'], name=op.f('fk_strike_to_user_associations_strike_id_strikes'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_strike_to_user_associations_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('strike_id', 'user_id', name=op.f('pk_strike_to_user_associations'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('strike_to_user_associations')
    # ### end Alembic commands ###
