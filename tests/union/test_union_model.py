from crud.helpers import exists_in_db
from models import Union


async def test_union_model_positive(db_session, union):
    """
    Позитивный тест модели Union.
    """
    assert await exists_in_db(db_session, Union, Union.id == union.id)
