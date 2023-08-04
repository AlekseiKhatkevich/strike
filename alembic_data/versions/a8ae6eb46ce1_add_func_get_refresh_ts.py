"""add func get_refresh_ts

Revision ID: a8ae6eb46ce1
Revises: 33b2a9ea513c
Create Date: 2023-08-04 12:24:25.685940

"""
from alembic import op
import sqlalchemy as sa
import functools

from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'a8ae6eb46ce1'
down_revision = '33b2a9ea513c'
branch_labels = None
depends_on = None

conn = functools.partial(op.get_bind)

"""
Функция получения времени последнего обновления материализованного представления по его имени.
"""


def upgrade() -> None:
    conn().execute(
        text(
            f"""         
CREATE OR REPLACE FUNCTION get_refresh_ts(varchar) returns timestamptz AS
    $$
    WITH
        pgdata AS (
                SELECT
                        setting AS path
                FROM
                        pg_settings
                WHERE
                        name = 'data_directory'
        ),
        path AS (
                SELECT
                        CASE
                                WHEN pgdata.separator = '/' THEN '/'    -- UNIX
                                ELSE '\'                                -- WINDOWS
                        END AS separator
                FROM
                        (SELECT SUBSTR(path, 1, 1) AS separator FROM pgdata) AS pgdata
        )
SELECT
        (pg_stat_file(pgdata.path||path.separator||pg_relation_filepath(ns.nspname||'.'||c.relname))).modification AS refresh
FROM
        pgdata,
        path,
        pg_class c
JOIN
        pg_namespace ns ON c.relnamespace=ns.oid
WHERE
        c.relkind='m' and c.relname = $1
;
    $$
    LANGUAGE SQL;   
            """
        ),
    )


def downgrade() -> None:
    conn().execute(
        text(
            f"""
             Drop function get_refresh_ts;
             """))
