import datetime

import factory

from models import UsedToken
from security.invitation import generate_invitation_token

__all__ = (
    'UsedTokenFactory',
)


class UsedTokenFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели использованного пригласительного токена.
    """
    user_id = None
    token = factory.LazyAttribute(
        lambda o: generate_invitation_token(o.future)
    )
    issued_at = factory.Faker('past_datetime', tzinfo=datetime.UTC)

    class Meta:
        model = UsedToken

    class Params:
        future = factory.Faker('future_datetime', tzinfo=datetime.UTC)
