from typing import Any, Awaitable, Callable, TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from models import UserRole
from tests.factories.strike import StrikeFactory, StrikeToUserAssociationFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import Strike, UserRole

register(StrikeFactory)
register(StrikeToUserAssociationFactory)


@pytest.fixture
async def strike(strike_factory: StrikeFactory,
                 create_instance_from_factory: Callable[['AsyncSession', 'Factory', Any, ...], Awaitable['Strike']],
                 ) -> Awaitable['Strike']:
    """
    Инстанс модели Strike сохраненный в БД.
    """
    return await create_instance_from_factory(strike_factory)


@pytest.fixture
async def strike_p(strike_factory: StrikeFactory,
                   create_instance_from_factory,
                   ) -> Callable[[Any, Any], Awaitable['Strike']]:
    """
    `strike` с возможностью передачи доп аргументов.
    """
    async def _inner(*args, **kwargs):
        return await create_instance_from_factory(strike_factory, *args, **kwargs)
    return _inner


@pytest.fixture
def strike_input_data(strike_factory, union, enterprise_instance) -> dict[str, Any]:
    """
    Минимально достаточные позитивные данные для сериалайзера.
    """
    strike_instance = strike_factory.build()
    return dict(
        duration=[strike_instance.duration.lower, strike_instance.duration.upper],
        planned_on_date=None,
        goals=strike_instance.goals,
        results=None,
        overall_num_of_employees_involved=strike_instance.overall_num_of_employees_involved,
        union_in_charge_id=union.id,
        enterprise=enterprise_instance.id,
        group=None,
        places=None,
        users_involved=None,
    )


@pytest.fixture
def user_role(faker) -> UserRole:
    """
    Рандомная роль юзера в м2м отношении со страйком.
    """
    return faker.random_element(elements=list(UserRole))
