import re

import pytest
import sqlalchemy.exc
from geoalchemy2 import WKTElement, WKBElement
from sqlalchemy import select

from crud.helpers import exists_in_db
from models import Place


async def test_place_positive(db_session, place):
    """
    Позитивный тест модели Place. Так же проверяем работоспособность collation
    RU_RU_CE_COLLATION_NAME.
    """
    assert await exists_in_db(
        db_session,
        Place,
        (Place.id == place.id) & (Place.name == place.name.upper())
    )


async def test_place_negative_exc_constraint(db_session, place_factory):
    """
    Негативный тест модели Place. Констрейнт close_points_exc_constraint не должен давать
    сохранить интстанс в БД у которого coordinates были бы в радиусе 100 метров и менее
    от любого другого уже существующего в БД инстанса Place.
    """
    instance1 = place_factory.build(coords_in_decimal=(22, 33))
    instance2 = place_factory.build(coords_in_decimal=(22.00000000001, 33.000000001))

    db_session.add(instance1)
    await db_session.commit()
    db_session.add(instance2)

    with pytest.raises(sqlalchemy.exc.IntegrityError, match='close_points_exc_constraint'):
        await db_session.commit()


async def test_coords_hr_property(place_factory, db_session):
    """
    Тест свойства coords_hr возвращающего координаты в decimal формате.
    """
    orig_coords = (22.1, 33.3)
    place = place_factory.build(coords_in_decimal=orig_coords)
    assert isinstance(place.coordinates, WKTElement)

    assert place.coords_hr == orig_coords

    db_session.add(place)
    await db_session.commit()

    await db_session.refresh(place)
    assert isinstance(place.coordinates, WKBElement)
    assert place.coords_hr == orig_coords


async def test_coords_hr_expression(place, db_session):
    """
    Тест свойства coords_hr возвращающего координаты в человеко читаемом формате в виде строки.
    Вариант получения через БД.
    """
    coords_hr = await db_session.scalar(
        select(Place.coords_hr)
    )
    assert re.match(r'^\d+°\d+.\d+"[N,S] \d+°\d+.\d+"[E,W]', coords_hr) is not None
