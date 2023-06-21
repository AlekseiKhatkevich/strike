from crud.helpers import exists_in_db
from models import Union


async def test_union_model_positive(db_session, union_factory):
    """
    Позитивный тест модели Union.
    """
    instance = await union_factory.create()
    assert await exists_in_db(db_session, Union, Union.id == instance.id)