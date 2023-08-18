import grpc

from crud.helpers import exists_in_db
from internal.database import async_session
from models import Conflict
from serializers.proto.compiled import conflicts_pb2


async def test_UpdateConflict_positive(two_conflicts, get_grpc_response):
    """
    Позитивный тест метода UpdateConflict обновления записи конфликта в БД.
    """
    conflict_to_update = two_conflicts[0]
    new_description = 'new description'

    request = conflicts_pb2.Conflict(
        id=conflict_to_update.id,
        type=conflict_to_update.type.name,
        enterprise_id=conflict_to_update.enterprise.id,
        description=new_description,
        results=conflict_to_update.results,
        success_rate=conflict_to_update.success_rate,
    )
    request.duration.lower.FromDatetime(conflict_to_update.duration.lower)
    request.duration.upper.FromDatetime(conflict_to_update.duration.upper)

    response, _, code, _ = await get_grpc_response('UpdateConflict', request)

    assert code == grpc.StatusCode.OK
    assert response.conflict.id == conflict_to_update.id
    assert isinstance(response.conflict, conflicts_pb2.Conflict)
    assert response.conflict.description == new_description

    async with async_session() as session:
        assert await exists_in_db(
            session,
            Conflict,
            (Conflict.id == response.conflict.id) & (Conflict.description == new_description)
        )
