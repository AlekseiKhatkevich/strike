import datetime
from concurrent import futures

import grpc

# from internal.database import async_session
from serializers.proto.compiled.conflicts_pb2_grpc import ConflictsServiceServicer, \
    ConflictsServiceStub, add_ConflictsServiceServicer_to_server
import asyncio
from grpc import aio
from loguru import logger
from serializers.proto.compiled.conflicts_pb2 import Conflict,ConflictExtraData, ConflictTypes, Duration, SingleConflictResponse


class ConflictsServicer(ConflictsServiceServicer):
    """

    """

    def CreateConflict(self, request, context):
        # async with async_session as session:
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


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  add_ConflictsServiceServicer_to_server(
      ConflictsServicer(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()



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
    serve()
