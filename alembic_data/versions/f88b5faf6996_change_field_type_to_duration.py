"""Change field type to duration

Revision ID: f88b5faf6996
Revises: dccae2fd7063
Create Date: 2023-06-16 10:27:05.348539

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f88b5faf6996'
down_revision = 'dccae2fd7063'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strikes', sa.Column('duration', postgresql.TSTZRANGE(), nullable=True))
    op.drop_column('strikes', 'started_at')
    op.drop_column('strikes', 'finished_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strikes', sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('strikes', sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.drop_column('strikes', 'duration')
    # ### end Alembic commands ###