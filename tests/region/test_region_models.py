from crud.helpers import exists_in_db
from models import Region


async def test_region_positive(region_factory, db_session):
    """
    Позитивный тест модели Region.
    """
    inst = region_factory.build()
    db_session.add(inst)
    await db_session.commit()

    assert await exists_in_db(db_session, Region, Region.name == inst.name)
