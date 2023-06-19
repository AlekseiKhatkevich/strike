"""Add link to creator into Strike

Revision ID: 7d1ab8a4b9b0
Revises: 44042a93ecfc
Create Date: 2023-06-19 12:20:00.893848

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '7d1ab8a4b9b0'
down_revision = '44042a93ecfc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('places', 'coordinates',
               existing_type=Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'),
               type_=Geography(geometry_type='POINT', from_text='ST_GeogFromText', name='geography'),
               existing_nullable=True)
    op.add_column('strikes', sa.Column('created_by_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(op.f('fk_strikes_created_by_id_users'), 'strikes', 'users', ['created_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_strikes_created_by_id_users'), 'strikes', type_='foreignkey')
    op.drop_column('strikes', 'created_by_id')
    op.alter_column('places', 'coordinates',
               existing_type=Geography(geometry_type='POINT', from_text='ST_GeogFromText', name='geography'),
               type_=Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'),
               existing_nullable=True)
    # ### end Alembic commands ###
