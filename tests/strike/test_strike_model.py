import pytest
from sqlalchemy import update

from crud.helpers import exists_in_db
from models import Strike
from sqlalchemy.exc import IntegrityError


async def test_strike_positive_basic(db_session, strike: Strike):
    """

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

    """
    with pytest.raises(ValueError):
        strike.overall_num_of_employees_involved = -1


async def test_strike_negative_overall_num_of_employees_involved_positive(db_session, strike: Strike):
    """

    """
    with pytest.raises(IntegrityError, match='overall_num_of_employees_involved_positive'):
        stmt = update(Strike).where(Strike.id == strike.id).values(
            overall_num_of_employees_involved=-1
        )
        await db_session.execute(stmt)


async def test_strike_negative_one_of_dates_is_not_null(db_session, strike_p):
    """

    """
    with pytest.raises(IntegrityError, match='one_of_dates_is_not_null'):
        await strike_p(duration=None)
