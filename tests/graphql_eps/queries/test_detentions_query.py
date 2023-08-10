from sqlalchemy import select

from graphql_related.main import schema
from internal.database import async_session
from models import Detention

EP_URL = '/graphql'


async def test_detentions_q(detention, db_session):
    """

    """
    query = """
    query Detentions {
    detentions {
        id
        duration
        name
        extraPersonalInfo
        needsMedicalAttention
        needsLawyer
        jailId
        charge
        transferredFromId
        relativeOrFriend
            }
        }  
    """
    response = await schema.execute(query)
    async with async_session() as session:
        a = await session.scalars(select(Detention))
        b = a.all()

    assert response.errors is None
    detentions = response.data['detentions']
    assert len(detentions) == 1