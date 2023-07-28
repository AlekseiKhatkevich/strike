import datetime

import factory
from sqlalchemy.dialects.postgresql import Range

from models import Detention, Jail

__all__ = (
    'JailFactory',
    'DetentionFactory',
)


class JailFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика крытой.
    """
    id = None
    name = factory.Faker('company', locale='ru_RU')
    address = factory.Faker('address', locale='ru_RU')
    region = factory.SubFactory('tests.factories.region.RegionFactory')

    class Meta:
        model = Jail


class DetentionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика похищения человека мусарами.
    """
    id = None
    duration = factory.LazyAttribute(
        lambda o: Range(
            o.detention_start,
            o.detention_end,
        )
    )
    name = factory.Faker('name')
    extra_personal_info = factory.Faker('sentence')
    needs_medical_attention = False
    needs_lawyer = False
    charge = None
    jail = factory.SubFactory(JailFactory)
    transferred_from_id = None
    relative_or_friend = factory.LazyAttribute(
        lambda o: f'{o.relative_name} -- {o.relative_phone}'
    )

    class Meta:
        model = Detention

    class Params:
        detention_start = factory.Faker(
            'date_time_this_month',
            before_now=True,
            tzinfo=datetime.UTC,
        )
        detention_end = None
        detention_duration = factory.Faker('pyint', min_value=1, max_value=30)
        done = factory.Trait(
            detention_end=datetime.datetime.now(tz=datetime.UTC)
        )
        relative_name = factory.Faker('name')
        relative_phone = factory.Faker('basic_phone_number')
