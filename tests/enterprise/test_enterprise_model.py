from crud.helpers import exists_in_db
from models import Enterprise


async def test_enterprise_model_positive(db_session, enterprise_instance):
    """
    Позитивный тест модели компании Enterprise.
    """
    assert await exists_in_db(db_session, Enterprise, Enterprise.id == enterprise_instance.id)
    assert await enterprise_instance.awaitable_attrs.region is not None
