"""trigger for event

Revision ID: 2820ad15278e
Revises: 8b54c5574c69
Create Date: 2023-07-31 15:53:07.504295

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '2820ad15278e'
down_revision = '8b54c5574c69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    trigger_function = text(
        """
    CREATE OR REPLACE FUNCTION detentions_event()
    RETURNS TRIGGER AS $$ DECLARE record RECORD; payload JSON; 
    BEGIN
    
      IF TG_OP = 'INSERT'
          THEN record = NEW;
          END IF;

      IF record = new  THEN
            payload = json_build_object('table', TG_TABLE_NAME, 'action', TG_OP, 'data', row_to_json(record));
            PERFORM pg_notify('detentions', payload::text);
            Raise Notice 'Created Detention notification';
        END IF;

      RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;   
        """
    )
    trigger = text(
        """
    CREATE TRIGGER notify_detention_event AFTER
    INSERT OR UPDATE OR DELETE ON detentions FOR EACH ROW EXECUTE
    PROCEDURE detentions_event();   
      """
    )

    connection.execute(trigger_function)
    connection.execute(trigger)


def downgrade() -> None:
    drop_trigger = text(""" drop trigger notify_detention_event on 
      detentions; """)
    connection = op.get_bind()
    connection.execute(drop_trigger)
