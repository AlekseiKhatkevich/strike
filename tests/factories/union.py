import datetime

import factory

from internal.database import async_session
from models import Union

__all__ = (
    'UnionFactory',
)


class UnionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Union (профсоюз).
    """
    id = None
    name = factory.Faker('company')
    is_yellow = False
    created_at = None

    class Meta:
        model = Union

    class Params:
        with_created_at = factory.Trait(
            created_at=datetime.datetime.now(tz=datetime.UTC),
        )
        with_id = factory.Trait(
            id=factory.Faker('pyint', min_value=1),
        )
