import asyncio

from asyncpg import Range
from grpc import aio, StatusCode
from loguru import logger
from pydantic import ValidationError

from config import settings
from crud.helpers import create_or_update_with_session_get
from internal.database import async_session
from serializers.conflicts import ConflictCreateSerializer
from serializers.proto.compiled.conflicts_pb2 import ConflictExtraData, SingleConflictResponse
from serializers.proto.compiled.conflicts_pb2_grpc import (
    ConflictsServiceServicer,
    add_ConflictsServiceServicer_to_server,
)


class ConflictsServicer(ConflictsServiceServicer):
    """

    """
    async def CreateConflict(self, request, context):
        try:
            conflict = ConflictCreateSerializer.model_validate(request)
        except ValidationError as err:
            await context.abort(
                code=StatusCode.INVALID_ARGUMENT,
                details=err.json(),
            )
        conflict_dict = conflict.model_dump()
        conflict_dict['duration'] = Range(conflict.duration.lower, conflict.duration.upper)
        async with async_session() as session:
            instance = await create_or_update_with_session_get(
                session,
                'Conflict',
                conflict_dict
            )
            response_pb = SingleConflictResponse()

            conflict_pb = instance.to_protobuf()
            response_pb.conflict.MergeFrom(conflict_pb)

            extra_data_pb = ConflictExtraData()
            extra_data_pb.created_at.FromDatetime(instance.created_at)
            response_pb.extra_data.MergeFrom(extra_data_pb)

            return response_pb


async def serve():
    server = aio.server()
    add_ConflictsServiceServicer_to_server(ConflictsServicer(), server)
    listen_addr = '[::]:' + settings.grpc_port
    server.add_insecure_port(listen_addr)
    logger.info(f'Starting server on {listen_addr}')
    await server.start()
    logger.info('Server has started')
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
