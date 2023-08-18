from typing import TYPE_CHECKING

import grpc_testing
import pytest
from pytest_factoryboy import register

from grpc_services.conflicts_server import ConflictsServicer
from internal.database import async_session
from serializers.proto.compiled import conflicts_pb2
from tests.factories.conflict import ConflictFactory

if TYPE_CHECKING:
    from models import Conflict
    from google.protobuf.message import Message
    from grpc import StatusCode

register(ConflictFactory)


@pytest.fixture(scope='session')
def grpc_server() -> grpc_testing.Server:
    """
    GRPC тестовый сервер.
    """
    servicers = {
        conflicts_pb2.DESCRIPTOR.services_by_name['ConflictsService']: ConflictsServicer()
    }
    test_server = grpc_testing.server_from_dictionary(
        servicers,
        grpc_testing.strict_real_time(),
    )
    return test_server


@pytest.fixture
async def two_conflicts(conflict_factory) -> 'Conflict':
    """
    2 конфликта.
    """
    async with async_session() as session:
        conflicts = conflict_factory.build_batch(size=2)
        session.add_all(conflicts)
        await session.commit()
        yield conflicts
        for c in conflicts:
            await session.delete(c)
        await session.commit()


@pytest.fixture
def get_grpc_response(grpc_server):
    """
    По переданному методу и реквесту отдает респонс, метадату, статус код и доп. инфо ресонса.
    """
    async def _response_and_stuff(
            method: str,
            request: 'Message',
    ) -> tuple['Message', str, 'StatusCode', str]:
        list_conflicts_method = grpc_server.invoke_unary_unary(
            method_descriptor=(
                conflicts_pb2.DESCRIPTOR.services_by_name['ConflictsService'].methods_by_name[method]
            ),
            invocation_metadata={},
            request=request,
            timeout=1,
        )

        response_coro, metadata, code, details = list_conflicts_method.termination()
        response = await response_coro
        return response, metadata, code, details

    return _response_and_stuff
