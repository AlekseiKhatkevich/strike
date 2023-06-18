"""Create gist extension

Revision ID: 30ed81dd1fee
Revises: dc4f663e709d
Create Date: 2023-06-18 10:54:47.303271

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '30ed81dd1fee'
down_revision = 'dc4f663e709d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(text("DROP EXTENSION IF EXISTS btree_gist;"))
    # ### end Alembic commands ###
