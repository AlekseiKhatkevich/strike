"""coords check constraint

Revision ID: 5142100d5388
Revises: 3b2701c77fc4
Create Date: 2023-06-28 12:47:42.757436

"""
from sqlalchemy.sql.expression import cast
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from geoalchemy2 import functions as ga_functions

from models import Place

# revision identifiers, used by Alembic.
revision = '5142100d5388'
down_revision = '3b2701c77fc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name='coordinates_limit',
        table_name='places',
        condition=(sa.func.abs(ga_functions.ST_X(cast(Place.coordinates, Geometry))) <= 180) &
                  (sa.func.abs(ga_functions.ST_Y(cast(Place.coordinates, Geometry))) <= 90)
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name='ck_places_coordinates_limit',
        table_name='places',
    )
