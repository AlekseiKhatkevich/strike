import datetime

import factory
from sqlalchemy.dialects.postgresql import Range

from models import Strike, StrikeToUserAssociation, UserRole
from tests.factories.place import PlaceFactory

__all__ = (
    'StrikeFactory',
    'StrikeToUserAssociationFactory',
)


class StrikeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Strike (забастовка).
    """
    planned_on_date = None
    goals = factory.Faker('text', max_nb_chars=128)
    results = None
    overall_num_of_employees_involved = factory.Faker('pyint', min_value=10, max_value=100_000)
    duration = factory.LazyAttribute(
        lambda o: Range(
            o.strike_start_dt,
            o.strike_start_dt + datetime.timedelta(days=o.strike_duration),
        )
    )
    created_by = factory.SubFactory('tests.factories.users.UserInDbFactory')
    enterprise = factory.SubFactory('tests.factories.enterprise.EnterpriseFactory')
    union = factory.SubFactory('tests.factories.union.UnionFactory')

    places = factory.lazy_attribute(
        lambda o: PlaceFactory.build_batch(size=o.num_places)
    )
    users_involved = factory.lazy_attribute(
        lambda o: StrikeToUserAssociationFactory.build_batch(
           size=o.num_users_associated,
        )
    )

    class Meta:
        model = Strike

    class Params:
        strike_start_dt = factory.Faker('date_time_this_month', after_now=True, tzinfo=datetime.UTC)
        strike_duration = factory.Faker('pyint', min_value=1, max_value=30)
        num_places = 2
        num_users_associated = 2


class StrikeToUserAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели StrikeToUserAssociation (м2м связь юзера с забастовкой)
    """
    user = factory.SubFactory('tests.factories.users.UserInDbFactory')
    role = factory.Faker('random_element', elements=list(UserRole))

    class Meta:
        model = StrikeToUserAssociation
