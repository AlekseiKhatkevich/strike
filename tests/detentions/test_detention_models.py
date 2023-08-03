import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from crud.helpers import is_instance_in_db
from models import DetentionMaterializedView


@pytest.fixture(params=['jail', 'detention'])
def instance(request):
    return request.getfixturevalue(request.param)


async def test_jail_model_positive(instance, db_session):
    """
    Позитивный тест создания и сохранения моделей Jail и Detention.
    """
    assert await is_instance_in_db(db_session, instance)


async def test_jail_negative_non_unique(db_session, jail, jail_factory, create_instance_from_factory):
    """
    Негативный тест модели Jail. Тест уникальности по name, region_id.
    """
    with pytest.raises(IntegrityError):
        await create_instance_from_factory(jail_factory, name=jail.name, region=jail.region)


async def test_detention_negative_duration_lower_none(detention_factory, create_instance_from_factory):
    """
    Негативный тест модели Detention. Поле "duration" не должно иметь открытую нижнюю границу
    диапазона.
    """
    with pytest.raises(IntegrityError, match='duration_has_start_dt'):
        await create_instance_from_factory(
            detention_factory,
            detention_start=None,
            detention_end=datetime.datetime.now(tz=datetime.UTC)
        )


async def test_detention_negative_exclude_c(detention_factory, detention, create_instance_from_factory):
    """
    Негативный тест модели Detention. Один и тот же человек не может сидеть в 2х разных
    крытых одновременно.
    """
    with pytest.raises(IntegrityError, match='duration_name_exc_constraint'):
        await create_instance_from_factory(
            detention_factory,
            duration=detention.duration,
            name=detention.name,
        )


async def test_DetentionMaterializedView_positive(db_session, detentions_for_view):
    """
    Позитивный тест материализованного представления DetentionMaterializedView.
    """
    jail1, jail2, detentions_jail1, detentions_jail2 = detentions_for_view

    jail1_cnts = await db_session.scalars(
        select(DetentionMaterializedView).filter_by(
            jail_id=jail1.id,
        )
    )
    jail1_cnts = jail1_cnts.all()
    assert len(jail1_cnts) == 2  # 2 days
    assert jail1_cnts[0].zk_count == jail1_cnts[-1].zk_count == 3  # 3 detentions

    jail2_cnts = await db_session.scalars(
        select(DetentionMaterializedView).filter_by(
            jail_id=jail2.id,
        )
    )
    jail2_cnts = jail2_cnts.all()
    assert len(jail2_cnts) == 2  # 2 days
    assert jail2_cnts[0].zk_count == jail2_cnts[-1].zk_count == 2  # 2 detentions
