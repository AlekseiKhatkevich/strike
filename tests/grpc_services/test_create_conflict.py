import grpc
import pytest

from crud.helpers import exists_in_db
from internal.database import async_session
from models import Conflict
from serializers.proto.compiled import conflicts_pb2

pytestmark = pytest.mark.usefixtures('truncate_db_func_scope')


async def test_CreateConflict_positive(get_grpc_response, conflict_factory, enterprise_factory):
    """
    Позитивный тест метода CreateConflict создания записи конфликта в БД.
    """
    async with async_session() as session:
        enterprise = enterprise_factory.build()
        session.add(enterprise)
        await session.commit()

        conflict = conflict_factory.build(enterprise=enterprise)
        request = conflicts_pb2.Conflict(
            type=conflict.type.name,
            enterprise_id=conflict.enterprise.id,
            description=conflict.description,
        )
        request.duration.lower.FromDatetime(conflict.duration.lower)
        request.duration.upper.FromDatetime(conflict.duration.upper)

        response, _, code, _ = await get_grpc_response('CreateConflict', request)

        assert code == grpc.StatusCode.OK
        pb_enum_name = conflicts_pb2.ConflictTypes.Name(response.conflict.type)
        assert pb_enum_name == conflict.type.name
        assert response.conflict.id is not None
        assert isinstance(response.conflict, conflicts_pb2.Conflict)
        assert await exists_in_db(session, Conflict, Conflict.id == response.conflict.id)
