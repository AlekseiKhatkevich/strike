"""Add Russian CE collation

Revision ID: 46bb8ffd1179
Revises: ea4877645996
Create Date: 2023-06-16 15:34:24.739840

"""
import functools

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from internal.constants import RU_RU_CE_COLLATION_NAME

# revision identifiers, used by Alembic.
revision = '46bb8ffd1179'
down_revision = 'ea4877645996'
branch_labels = None
depends_on = None


conn = functools.partial(op.get_bind)


def upgrade() -> None:
    conn().execute(
        text(
            f"""
            CREATE COLLATION {RU_RU_CE_COLLATION_NAME} (
            PROVIDER = icu,
            LOCALE = 'ru-RU-u-ks-level2',
            DETERMINISTIC = FALSE
            );
            """
        ),
    )


def downgrade() -> None:
    conn().execute(
        text(
            f"""
            drop collation {RU_RU_CE_COLLATION_NAME};
            """
        )
    )
