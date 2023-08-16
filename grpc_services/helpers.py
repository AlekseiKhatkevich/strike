from typing import TYPE_CHECKING

from grpc import StatusCode
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from crud.helpers import get_text_from_integrity_error

if TYPE_CHECKING:
    from grpc.aio import ServicerContext

__all__ = (
    'GRPCErrorHandler',
)


class GRPCErrorHandler:
    """
    Перехватывает полученные исключения в сервисах GRPC и по факту их перехвата
    завершает запрос с передачей исключения на клиента.
    """
    def __init__(self, context: 'ServicerContext'):
        self.context = context

    # noinspection PyTypeChecker
    @staticmethod
    def get_exc_details_to_report(exc_val: Exception) -> dict[StatusCode, str]:
        match exc_val:
            case ValidationError():
                return dict(
                    code=StatusCode.INVALID_ARGUMENT,
                    details=exc_val.json(),
                )
            case IntegrityError():
                return dict(
                    code=StatusCode.INTERNAL,
                    details=get_text_from_integrity_error(exc_val),
                )
            case _:
                return dict(
                    code=StatusCode.INTERNAL,
                    details=str(exc_val),
                )

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            logger.exception(exc_val)
            await self.context.abort(
                **self.get_exc_details_to_report(exc_val)
            )
