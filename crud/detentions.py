# https://markandruth.co.uk/2022/12/20/using-postgres-notify-with-placeholders
# https://wuilly.com/2019/10/real-time-notifications-with-python-and-postgres/

#  CREATE OR REPLACE FUNCTION detentions_event()
#   RETURNS TRIGGER AS $$ DECLARE record RECORD; payload JSON;
#   BEGIN
#       IF TG_OP = 'INSERT'
#           THEN record = NEW;
#           END IF;
#     payload = json_build_object('table', TG_TABLE_NAME, 'action', TG_OP, 'data', row_to_json(record));
#
#       IF record == new  THEN
#             PERFORM pg_notify('orders', payload::text); ;
#             Raise Notice 'Created Detention notification';
#         END IF;
#
#       RETURN NULL; END;
#   $$ LANGUAGE plpgsql;
#
#
# CREATE TRIGGER notify_detention_event AFTER
#   INSERT OR UPDATE OR DELETE ON detentions FOR EACH ROW EXECUTE
#   PROCEDURE detentions_event();