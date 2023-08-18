import grpc_testing
import pytest
from pytest_factoryboy import register

from grpc_services.conflicts_server import ConflictsServicer
from serializers.proto.compiled import conflicts_pb2
from tests.factories.conflict import ConflictFactory

register(ConflictFactory)


@pytest.fixture(scope='module')
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
