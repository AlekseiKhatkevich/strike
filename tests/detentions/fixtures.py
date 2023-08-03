import datetime
from typing import Any, Awaitable, Callable, TYPE_CHECKING
from zoneinfo import ZoneInfo

import pytest
from pytest_factoryboy import register

from models import Detention, DetentionMaterializedView, Jail
from tests.factories.detention import DetentionFactory, JailFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from factory import Factory

register(JailFactory)
register(DetentionFactory)


@pytest.fixture
async def jail(jail_factory: JailFactory,
               create_instance_from_factory: Callable[['AsyncSession', 'Factory', Any, ...], Awaitable['Jail']],
               ) -> Awaitable['Jail']:
    """
    Инстанс модели Jail сохраненный в БД.
    """
    return await create_instance_from_factory(jail_factory)


@pytest.fixture
async def detention(detention_factory: DetentionFactory,
                    create_instance_from_factory: Callable[
                        ['AsyncSession', 'Factory', Any, ...], Awaitable['Detention']],
                    ) -> Awaitable['Detention']:
    """
    Инстанс модели Detention сохраненный в БД.
    """
    return await create_instance_from_factory(detention_factory)


@pytest.fixture
async def detentions_for_view(db_session,
                              jail_factory,
                              detention_factory,
                              ) -> tuple[
    Jail, Jail, list[Detention, ...], list[Detention, ...]
]:
    """
    Пачка задержаний для создания представления DetentionMaterializedView
    """
    jail1, jail2 = jail_factory.build_batch(size=2)
    detentions_jail1 = detention_factory.build_batch(
        size=3,
        jail=jail1,
        detention_start=datetime.datetime(2020, 1, 1, tzinfo=ZoneInfo('UTC')),
        detention_end=datetime.datetime(2020, 1, 2, tzinfo=ZoneInfo('UTC')),
    )
    detentions_jail2 = detention_factory.build_batch(
        size=2,
        jail=jail2,
        detention_start=datetime.datetime(2021, 1, 1, tzinfo=ZoneInfo('UTC')),
        detention_end=datetime.datetime(2021, 1, 2, tzinfo=ZoneInfo('UTC')),
    )
    db_session.add_all([*detentions_jail1, *detentions_jail2])
    await db_session.commit()
    await DetentionMaterializedView.refresh(db_session, False)

    return jail1, jail2, detentions_jail1, detentions_jail2
