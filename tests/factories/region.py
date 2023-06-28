import factory
from geoalchemy2 import WKTElement

from internal.database import async_session
from models import Region
from models.initial_data import RU_regions
from tests.factories.async_helpers import AsyncSQLAlchemyModelFactory

__all__ = (
    'RegionFactory',
)


class RegionFactory(AsyncSQLAlchemyModelFactory):
    """
    Фабрика модели Region (регион РФ).
    """
    name = factory.Iterator(RU_regions.names)
    contour = WKTElement(
        'MULTIPOLYGON(((0 0,4 0,4 4,0 4,0 0)),((1 1,2 1,2 2,1 2,1 1)), ((-1 -1,-1 -2,-2 -2,-2 -1,-1 -1)))',
        srid=4326,
    )

    class Meta:
        model = Region
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'
