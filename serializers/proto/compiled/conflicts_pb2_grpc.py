# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from serializers.proto.compiled import conflicts_pb2 as conflicts__pb2


class ConflictsServiceStub(object):
    """компиляция
    python -m grpc_tools.protoc -I /usr/include/google/protobuf/timestamp.proto
    --python_out=./compiled --proto_path=/home/hardcase/PycharmProjects/strike/serializers/proto/
    --pyi_out=./compiled --grpc_python_out=./compiled  conflicts.proto

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateConflict = channel.unary_unary(
                '/strike.ConflictsService/CreateConflict',
                request_serializer=conflicts__pb2.Conflict.SerializeToString,
                response_deserializer=conflicts__pb2.SingleConflictResponse.FromString,
                )
        self.DeleteConflict = channel.unary_unary(
                '/strike.ConflictsService/DeleteConflict',
                request_serializer=conflicts__pb2.SingleIdRequest.SerializeToString,
                response_deserializer=conflicts__pb2.EmptyResponse.FromString,
                )


class ConflictsServiceServicer(object):
    """компиляция
    python -m grpc_tools.protoc -I /usr/include/google/protobuf/timestamp.proto
    --python_out=./compiled --proto_path=/home/hardcase/PycharmProjects/strike/serializers/proto/
    --pyi_out=./compiled --grpc_python_out=./compiled  conflicts.proto

    """

    def CreateConflict(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteConflict(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConflictsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateConflict': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateConflict,
                    request_deserializer=conflicts__pb2.Conflict.FromString,
                    response_serializer=conflicts__pb2.SingleConflictResponse.SerializeToString,
            ),
            'DeleteConflict': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteConflict,
                    request_deserializer=conflicts__pb2.SingleIdRequest.FromString,
                    response_serializer=conflicts__pb2.EmptyResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'strike.ConflictsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ConflictsService(object):
    """компиляция
    python -m grpc_tools.protoc -I /usr/include/google/protobuf/timestamp.proto
    --python_out=./compiled --proto_path=/home/hardcase/PycharmProjects/strike/serializers/proto/
    --pyi_out=./compiled --grpc_python_out=./compiled  conflicts.proto

    """

    @staticmethod
    def CreateConflict(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/strike.ConflictsService/CreateConflict',
            conflicts__pb2.Conflict.SerializeToString,
            conflicts__pb2.SingleConflictResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteConflict(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/strike.ConflictsService/DeleteConflict',
            conflicts__pb2.SingleIdRequest.SerializeToString,
            conflicts__pb2.EmptyResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
