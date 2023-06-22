from crud.helpers import exists_in_db
from models import Strike


async def test_strike_positive_basic(db_session, strike_):
    """

    """
    assert await exists_in_db(db_session, Strike, Strike.id == strike_.id)