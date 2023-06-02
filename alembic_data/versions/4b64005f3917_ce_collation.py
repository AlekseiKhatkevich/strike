"""CE collation

Revision ID: 4b64005f3917
Revises: 8f321f4db427
Create Date: 2023-06-02 10:29:16.009959

"""
import functools

from alembic import op
from sqlalchemy.sql import text

from internal.constants import EN_US_CE_COLLATION_NAME

# revision identifiers, used by Alembic.
revision = '4b64005f3917'
down_revision = '8f321f4db427'
branch_labels = None
depends_on = None

conn = functools.partial(op.get_bind)


def upgrade() -> None:
    conn().execute(
        text(
            f"""
            CREATE COLLATION {EN_US_CE_COLLATION_NAME} (
            PROVIDER = icu,
            LOCALE = 'en-US-u-ks-level2',
            DETERMINISTIC = FALSE
            );
            """
        ),
    )


def downgrade() -> None:
    conn().execute(
        text(
            f"""
            drop collation {EN_US_CE_COLLATION_NAME};
            """
        )
    )
