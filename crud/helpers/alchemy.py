from functools import wraps
from typing import TYPE_CHECKING, Callable, Any

from sqlalchemy import select, inspect

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from internal.database import Base
    from sqlalchemy.sql.elements import OperatorExpression


__all__ = (
    'exists_in_db',
    'commit_if_not_in_transaction',
)


def commit_if_not_in_transaction(func: Callable) -> Callable:
    """
    Используется для функций которые осуществляют DSL SQL.
    Если в сессии не открыта транзакция, то делаем коммит для того, чтобы за нами можно было
    дальше открыть транзакцию если нужно.
    """
    @wraps(func)
    async def wrapper(session: 'AsyncSession', *args, **kwargs) -> Any:
        transaction_already = session.in_transaction()
        res = await func(session, *args, **kwargs)
        if not transaction_already:
            await session.commit()
        return res
    return wrapper


@commit_if_not_in_transaction
async def exists_in_db(session: 'AsyncSession',
                       model: 'Base',
                       condition: 'OperatorExpression',
                       ) -> bool:
    """
    :param session: Сессия БД
    :param model: Модель
    :param condition: Условия фильтрации кверисета.
    :return: Есть ли хотя бы одна запись в БД удовлетворяющая условиям.
    """
    pk = inspect(model).primary_key
    pk_name = pk[0].name
    stmt = select(getattr(model, pk_name)).where(condition).limit(1)
    return await session.scalar(stmt) is not None
