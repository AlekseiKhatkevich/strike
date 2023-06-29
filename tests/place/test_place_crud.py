import pytest

from crud.helpers import exists_in_db
from crud.places import create_or_update_place, delete_place
from models import Place


async def test_create_or_update_place_positive(db_session, place_factory):
    """
    Позитивный тест ф-ции create_place сохранения инстанса Place в БД.
    """
    place = place_factory.build()

    place_saved = await create_or_update_place(db_session, place)

    # assert place in db_session
    assert await exists_in_db(db_session, Place, Place.id == place_saved.id)


async def test_create_or_update_place_negative(db_session, place_factory, place):
    """
    Негативный тест ф-ции create_place сохранения инстанса Place в БД.
    В случае если сохраняемые координаты находятся в радиусе 100м. от уже сохраненной
    координаты то возбуждается исключение.
    """
    place_2_save = place_factory.build(coords_in_decimal=place.coords_hr)

    with pytest.raises(ValueError):
        await create_or_update_place(db_session, place_2_save)


async def test_create_or_update_place_update(db_session, place):
    """
    Проверяем вариант работы с обновлением.
    """
    place_2_merge = Place(
        id=place.id,
        name='new_name',
        address=place.address,
        coordinates=None,
    )

    await create_or_update_place(db_session, place_2_merge)

    assert await exists_in_db(
        db_session,
        Place,
        (Place.id == place.id) & (Place.name == place_2_merge.name) & (Place.coordinates == None)
    )


@pytest.mark.parametrize('attrs', [('id',), ('name',)])
async def test_delete_place(attrs, db_session, place):
    """
    Позитивный тест ф-йии delete_place. Должна удалять запись Place либо по id либо по
    name.
    """
    lookup_kwargs = {attr: getattr(place, attr) for attr in attrs}

    deleted = await delete_place(db_session, lookup_kwargs)

    assert deleted
    assert not await exists_in_db(db_session, Place, Place.id == place.id)
