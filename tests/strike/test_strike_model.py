import pytest
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from crud.helpers import exists_in_db
from models import Strike, StrikeToItself


async def test_strike_positive_basic(db_session, strike: Strike):
    """
    Позитивный тест модели Strike. Должна быть создана запись в БД в случае если все ок.
    """
    assert await exists_in_db(db_session, Strike, Strike.id == strike.id)
    assert None not in {
        strike.created_by_id,
        strike.union_in_charge_id,
        strike.enterprise_id,
    }
    assert strike.places
    assert strike.users_involved
    assert strike.enterprise
    assert await strike.awaitable_attrs.user_ids == [ui.user_id for ui in strike.users_involved]


async def test_strike_negative_model_level_validation(db_session, strike: Strike):
    """
    Негативный тест модели Strike. Если поле overall_num_of_employees_involved < 1 то
    должно быть возбужденно исключение.
    """
    with pytest.raises(ValueError):
        strike.overall_num_of_employees_involved = -1


async def test_strike_negative_overall_num_of_employees_involved_positive(db_session, strike: Strike):
    """
    Негативный тест модели Strike. Если поле overall_num_of_employees_involved < 1 то
    должно быть возбужденно исключение (на уровне БД).
    """
    with pytest.raises(IntegrityError, match='overall_num_of_employees_involved_positive'):
        stmt = update(Strike).where(Strike.id == strike.id).values(
            overall_num_of_employees_involved=-1
        )
        await db_session.execute(stmt)


async def test_strike_negative_one_of_dates_is_not_null(strike_p):
    """
    Негативный тест модели Strike. Если оба 2 поля planned_on_date и duration Null -
    то возбуждается исключение на уровне БД.
    """
    with pytest.raises(IntegrityError, match='one_of_dates_is_not_null'):
        await strike_p(duration=None)


async def test_strike_negative_duration_enterprise_exc_constraint(db_session, strike: Strike, strike_p):
    """
    Негативный тест модели Strike. Если диапазон в duration пересекает такой же диапазон
    в какой-либо другой записи модели Strike в БД и у обоих этих двух записей одинаковая
    компания - то возбуждается исключение на уровне БД.
    """
    with pytest.raises(IntegrityError, match='duration_enterprise_exc_constraint'):
        await strike_p(enterprise=strike.enterprise, duration=strike.duration)


async def test_strike_group(db_session, strike, strike_p):
    """
    Позитивный тест модели Strike. Возможность создавать группы забастовок через м2м на себя.
    """
    strike2 = await strike_p()
    group = await strike.awaitable_attrs.group
    group.append(strike2)
    await db_session.commit()

    assert await exists_in_db(
        db_session,
        StrikeToItself,
        (StrikeToItself.strike_left_id == strike.id) & (StrikeToItself.strike_right_id == strike2.id)
    )
