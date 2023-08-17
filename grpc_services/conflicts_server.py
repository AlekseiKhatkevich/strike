from typing import Any, TYPE_CHECKING, Type

import aiorun
from asyncpg import Range
import grpc
from grpc._compression import Gzip
from grpc_reflection.v1alpha import reflection
from loguru import logger

from config import settings
from crud.conflicts import list_conflicts
from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from grpc_services.helpers import GRPCErrorHandler
from grpc_services.interceptors import AuthInterceptor
from internal.database import async_session
from models import Conflict
from serializers.conflicts import (
    ConflictCreateSerializer,
    ConflictUpdateSerializer,
    ConflictsRequestedConditionsSerializer,
)
from serializers.proto.compiled.conflicts_pb2 import (
    Conflict as ConflictPB,
    ConflictExtraData,
    DESCRIPTOR,
    EmptyResponse,
    MultipleConflictsResponse,
    SingleConflictResponse,
)
from serializers.proto.compiled.conflicts_pb2_grpc import (
    ConflictsServiceServicer,
    add_ConflictsServiceServicer_to_server,
)

if TYPE_CHECKING:
    from grpc.aio import ServicerContext


class ConflictsServicer(ConflictsServiceServicer):
    """
    Создание записи модели Conflict.
    """
    @staticmethod
    def get_conflict_dict(request: ConflictPB,
                          serializer: Type[ConflictCreateSerializer] | Type[ConflictUpdateSerializer],
                          ) -> dict[str, Any]:
        """
        Пропихиваем сырые данные с буфера в сериалайзер, затем получаем словарь с
        данными.
        """
        conflict = serializer.model_validate(request)
        conflict_dict = conflict.model_dump()
        conflict_dict['duration'] = Range(conflict.duration.lower, conflict.duration.upper)
        return conflict_dict

    @staticmethod
    def create_single_conflict_response_pb(instance: Conflict) -> SingleConflictResponse:
        """
        Создаем респонс с одним созданным или обновленным Conflict.
        """
        response_pb = SingleConflictResponse()

        conflict_pb = instance.to_protobuf()
        response_pb.conflict.MergeFrom(conflict_pb)

        extra_data_pb = ConflictExtraData()
        extra_data_pb.created_at.FromDatetime(instance.created_at)
        if instance.updated_at is not None:
            extra_data_pb.updated_at.FromDatetime(instance.updated_at)
        response_pb.extra_data.MergeFrom(extra_data_pb)

        return response_pb

    async def CreateOrUpdateConflict(self,
                                     context: 'ServicerContext',
                                     data: dict[str, Any],
                                     ) -> SingleConflictResponse:
        """
        Создает или обновляет 1 запись Conflict.
        """
        async with GRPCErrorHandler(context), async_session() as session:
            instance = await create_or_update_with_session_get(
                session, 'Conflict', data,
            )
            return self.create_single_conflict_response_pb(instance)

    async def CreateConflict(self, request, context):
        """
        Создание записи Conflict в БД.
        """
        data = self.get_conflict_dict(request, ConflictCreateSerializer)
        return await self.CreateOrUpdateConflict(context, data)

    async def DeleteConflict(self, request, context):
        """
        Удаление записи Conflict по id.
        """
        async with GRPCErrorHandler(context), async_session() as session:
            await delete_via_sql_delete(
                session,
                Conflict,
                Conflict.id == request.id,
            )
            return EmptyResponse()

    async def UpdateConflict(self, request, context):
        """
        Обновление 1 записи Conflict.
        """
        data = self.get_conflict_dict(request, ConflictUpdateSerializer)
        return await self.CreateOrUpdateConflict(context, data)

    async def ListConflicts(self, request, context):
        """
        Отдает список конфликтов по переданным условиям фильтрации.
        """
        async with GRPCErrorHandler(context), async_session() as session:
            conditions = ConflictsRequestedConditionsSerializer.model_validate(request)
            conflicts = await list_conflicts(session, conditions)

            response = MultipleConflictsResponse()
            response.conflicts.MergeFrom(
                self.create_single_conflict_response_pb(c) for c in conflicts
            )
            return response


async def serve():
    server = grpc.aio.server(interceptors=(AuthInterceptor(),), compression=Gzip)
    add_ConflictsServiceServicer_to_server(ConflictsServicer(), server)
    listen_addr = '[::]:' + settings.grpc_port
    service_names = (
        DESCRIPTOR.services_by_name['ConflictsService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    server.add_insecure_port(listen_addr)
    logger.info(f'Starting server on {listen_addr}')
    await server.start()
    logger.info('Server has started')
    await server.wait_for_termination()


if __name__ == '__main__':
    aiorun.run(serve(), use_uvloop=True)
