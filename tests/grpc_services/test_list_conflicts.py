import grpc
import pytest
import grpc_testing
from grpc_services.conflicts_server import ConflictsServicer
from serializers.proto.compiled import conflicts_pb2
from serializers.proto.compiled.conflicts_pb2_grpc import ConflictsServiceServicer

# https://github.com/alexykot/grpcio-test-example/blob/master/example/test_greeter_server.py


async def test_ListConflicts():
    servicers = {
        conflicts_pb2.DESCRIPTOR.services_by_name['ConflictsService']: ConflictsServicer()
    }
    test_server = grpc_testing.server_from_dictionary(
        servicers,
        grpc_testing.strict_real_time(),
    )

    request = conflicts_pb2.MultipleConflictsRequest()

    sayhello_method = test_server.invoke_unary_unary(
        method_descriptor=(
            conflicts_pb2.DESCRIPTOR.services_by_name['ConflictsService'].methods_by_name['ListConflicts']
        ),
        invocation_metadata={},
        request=request,
        timeout=1,
    )

    response, metadata, code, details = sayhello_method.termination()
    response = await response

    assert response.conflicts == []
    assert code == grpc.StatusCode.OK
