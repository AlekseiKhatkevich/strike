from typing import TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from internal.database import Base
    from sqlalchemy.sql.elements import OperatorExpression


__all__ = (
    'exists_in_db',
)


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
    transaction_already = session.in_transaction()
    stmt = select(getattr(model, 'id')).where(condition).limit(1)
    exists = bool(await session.scalar(stmt))
    #  если в сессии не открыта транзакция, то делаем коммит для того, чтобы за нами можно было
    #  дальше открыть транзакцию если нужно.
    if not transaction_already:
        await session.commit()
    return exists
