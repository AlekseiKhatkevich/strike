import asyncio
import datetime

from grpc import aio
from loguru import logger

from config import settings
from internal.database import async_session
from serializers.conflicts import ConflictCreateSerializer
from serializers.proto.compiled.conflicts_pb2 import (
    Conflict,
    ConflictExtraData,
    ConflictTypes,
    SingleConflictResponse,
)
from serializers.proto.compiled.conflicts_pb2_grpc import (
    ConflictsServiceServicer,
    add_ConflictsServiceServicer_to_server,
)


class ConflictsServicer(ConflictsServiceServicer):
    """

    """
    async def CreateConflict(self, request, context):
        conflict = ConflictCreateSerializer.model_validate(request)
        async with async_session() as session:
            pass
            # conflict = Conflict()
            # conflict.id = 1
            # conflict.type = ConflictTypes.LAYOFF
            #
            # now = datetime.datetime.now(tz=datetime.UTC)
            # conflict.duration.lower.FromDatetime(now)
            # conflict.duration.upper.FromDatetime(now + datetime.timedelta(days=10))
            #
            # conflict.description = 'test'
            #
            # sr = SingleConflictResponse()
            # sr.conflict.MergeFrom(conflict)
            #
            # ed = ConflictExtraData()
            # ed.created_at.FromDatetime(now)
            #
            # sr.extra_data.MergeFrom(ed)
            #
            # return sr


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
