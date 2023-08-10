import datetime

import strawberry

__all__ = (
    'ZKTransferInput',
)


@strawberry.input
class ZKTransferInput:
    """
    Для мутации zk_transfer.
    detention_id - откуда переводим.
    jail - куда переводим
    transfer_dt - время совершения перевода
    detention_upper - до какого времени будет идти заключение в крытой куда переводим.
    """
    detention_id: int = strawberry.field(description='Who is transferred')
    jail: int = strawberry.field(description='Transfer poor motherfucker where exactly')
    transfer_dt: datetime.datetime = strawberry.field(description='Transfer datetime')
    detention_upper: datetime.datetime | None = strawberry.field(description='Extend cell time if needed.')
