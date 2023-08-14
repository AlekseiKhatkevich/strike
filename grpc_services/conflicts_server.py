import datetime

from internal.database import async_session
from serializers.proto.compiled.conflicts_pb2_grpc import ConflictsServiceServicer
import asyncio
from grpc import aio
from loguru import logger
from serializers.proto.compiled.conflicts_pb2 import Conflict,ConflictExtraData, ConflictTypes, Duration, SingleConflictResponse


class RouteGuideServicer(ConflictsServiceServicer):
    """

    """

    async def CreateConflict(self, request, context):
        with async_session as session:
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
