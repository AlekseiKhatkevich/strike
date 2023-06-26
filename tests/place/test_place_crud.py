import pytest

from crud.helpers import exists_in_db
from crud.places import create_place
from models import Place


async def test_create_place_positive(db_session, place_factory):
    """
    Позитивный тест ф-ции create_place сохранения инстанса Place в БД.
    """
    place = place_factory.build()

    place_saved = await create_place(db_session, place)

    assert place in db_session
    assert await exists_in_db(db_session, Place, Place.id == place_saved.id)


async def test_create_place_negative(db_session, place_factory, place):
    """
    Негативный тест ф-ции create_place сохранения инстанса Place в БД.
    В случае если сохраняемые координаты находятся в радиусе 100м. от уже сохраненной
    координаты то возбуждается исключение.
    """
    place_2_save = place_factory.build(coords_in_decimal=place.coords_hr)

    with pytest.raises(ValueError):
        await create_place(db_session, place_2_save)
