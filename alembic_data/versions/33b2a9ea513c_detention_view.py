"""detention_view

Revision ID: 33b2a9ea513c
Revises: 2820ad15278e
Create Date: 2023-08-02 14:51:58.910259

"""
from alembic import op

from models import DetentionMaterializedView

# revision identifiers, used by Alembic.
revision = '33b2a9ea513c'
down_revision = '2820ad15278e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    DetentionMaterializedView.create(op)


def downgrade() -> None:
    DetentionMaterializedView.drop(op)
