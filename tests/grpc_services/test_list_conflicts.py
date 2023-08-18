import grpc

from serializers.proto.compiled import conflicts_pb2


# https://github.com/alexykot/grpcio-test-example/blob/master/example/test_greeter_server.py


async def test_ListConflicts(grpc_server):

    request = conflicts_pb2.MultipleConflictsRequest()

    sayhello_method = grpc_server.invoke_unary_unary(
        method_descriptor=(
            conflicts_pb2.DESCRIPTOR.services_by_name['ConflictsService'].methods_by_name['ListConflicts']
        ),
        invocation_metadata={},
        request=request,
        timeout=1,
    )

    response_coro, metadata, code, details = sayhello_method.termination()
    response = await response_coro

    assert response.conflicts == []
    assert code == grpc.StatusCode.OK
