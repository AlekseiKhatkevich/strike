"""Strike creation ts

Revision ID: a257a4f02014
Revises: 677bd6fa315f
Create Date: 2023-07-26 15:40:33.339107

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = 'a257a4f02014'
down_revision = '677bd6fa315f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strikes', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strikes', 'created_at')
    # ### end Alembic commands ###
