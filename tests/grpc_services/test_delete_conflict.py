import grpc

from crud.helpers import exists_in_db
from internal.database import async_session
from models import Conflict
from serializers.proto.compiled import conflicts_pb2


async def test_DeleteConflict_positive(get_grpc_response, two_conflicts):
    """
    Позитивный тест метода DeleteConflict удаляющего конфликт.
    """
    id_to_del = two_conflicts[0].id
    request = conflicts_pb2.SingleIdRequest(id=id_to_del)

    response, _, code, _ = await get_grpc_response('DeleteConflict', request)

    assert code == grpc.StatusCode.OK
    assert isinstance(response, conflicts_pb2.EmptyResponse)

    async with async_session() as session:
        assert not await exists_in_db(session, Conflict, Conflict.id == id_to_del)
