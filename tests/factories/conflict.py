import datetime
import random

import factory
from factory.fuzzy import FuzzyChoice
from sqlalchemy.dialects.postgresql import Range

from internal.database import async_session
from models import Conflict, ConflictTypes
from tests.factories.async_helpers import AsyncSQLAlchemyModelFactory

__all__ = (
    'ConflictFactory',
)


class ConflictFactory(AsyncSQLAlchemyModelFactory):
    """
    Конфликт.
    """
    id = None
    type = FuzzyChoice(ConflictTypes)
    duration = factory.LazyAttribute(
        lambda o: Range(
            o.duration_start,
            o.duration_start + datetime.timedelta(days=o.duration_duration),
        )
    )
    enterprise = factory.SubFactory('tests.factories.enterprise.EnterpriseFactory')
    description = factory.Faker('text')
    results = factory.Faker('text')
    success_rate = factory.Faker('pyfloat', min_value=0, max_value=1)

    class Meta:
        model = Conflict
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'  # попробовать flush

    class Params:
        duration_start = factory.Faker(
            'date_time_this_month',
            before_now=True,
            tzinfo=datetime.UTC,
        )
        duration_duration = random.randint(1, 10)
