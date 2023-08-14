import asyncio
import datetime

import grpc
from grpc import aio
from loguru import logger

from serializers.proto.compiled.conflicts_pb2 import Conflict, ConflictExtraData, ConflictTypes, SingleConflictResponse
from internal.database import async_session
from serializers.proto.compiled.conflicts_pb2_grpc import ConflictsServiceServicer, \
    ConflictsServiceStub, add_ConflictsServiceServicer_to_server


class ConflictsServicer(ConflictsServiceServicer):
    """

    """

    async def CreateConflict(self, request, context):
        async with async_session() as session:
            conflict = Conflict()
            conflict.id = 1
            conflict.type = ConflictTypes.LAYOFF

            now = datetime.datetime.now(tz=datetime.UTC)
            conflict.duration.lower.FromDatetime(now)
            conflict.duration.upper.FromDatetime(now + datetime.timedelta(days=10))

            conflict.description = 'test'

            sr = SingleConflictResponse()
            sr.conflict.MergeFrom(conflict)

            ed = ConflictExtraData()
            ed.created_at.FromDatetime(now)

            sr.extra_data.MergeFrom(ed)

            return sr


async def serve():
    server = aio.server()
    add_ConflictsServiceServicer_to_server(ConflictsServicer(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logger.info("Starting server on %s" % listen_addr)
    await server.start()
    await server.wait_for_termination()


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ConflictsServiceStub(channel)

        conflict = Conflict()
        conflict.id = 1
        conflict.type = ConflictTypes.LAYOFF

        now = datetime.datetime.now(tz=datetime.UTC)
        conflict.duration.lower.FromDatetime(now)
        conflict.duration.upper.FromDatetime(now + datetime.timedelta(days=10))

        conflict.description = 'test'

        resp = stub.CreateConflict(conflict)
        print('HERE228', resp)


if __name__ == "__main__":
    asyncio.run(serve())
