"""KafKaRoutes add field

Revision ID: 49afcf21dc4c
Revises: 20558ef6f454
Create Date: 2023-08-29 10:19:16.000747

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '49afcf21dc4c'
down_revision = '20558ef6f454'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kafka_routes', sa.Column('num_points', sa.Integer(), nullable=False))


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('kafka_routes', 'num_points')
    # ### end Alembic commands ###