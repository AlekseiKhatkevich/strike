from functools import wraps
from typing import Any, Callable, TYPE_CHECKING, Type, TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.dialects.postgresql import insert

from internal.database import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.elements import OperatorExpression

__all__ = (
    'exists_in_db',
    'commit_if_not_in_transaction',
    'create_or_update_with_on_conflict',
    'create_or_update_with_session_get',
)

MODEL_T = TypeVar('MODEL_T', bound='Base')


def get_pk_name(model: 'Base') -> str:
    """
    Название первичного ключа модели.
    """
    pk_inst = inspect(model).primary_key
    return pk_inst[0].name


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
    stmt = select(getattr(model, get_pk_name(model))).where(condition).limit(1)
    return await session.scalar(stmt) is not None


async def create_or_update_with_on_conflict(session: 'AsyncSession',
                                            model: Type[MODEL_T],
                                            lookup_kwargs: dict[str, Any],
                                            update_kwargs: dict[str, Any],
                                            unique_fields: list[str, ...],
                                            ) -> MODEL_T:
    """
    Создает запись в БД или обновляет уже существующую.
    :param unique_fields: List с уникальным (ими) полями, по которым определяется конфликт.
    :param session: Сессия БД.
    :param model: Модель SQLAlchemy
    :param lookup_kwargs: словарь имя поля: значение по которым ищется непосредственно сама запись в БД
    :param update_kwargs: словарь имя поля: значение с данными которые будет непосредственно обновлены.
    :return: Инстанс обновленной или созданной модели.

    Пример обновления:
        await create_or_update_with_on_conflict(session, Union, dict(name='test2'), dict(is_yellow=False), [Union.name])
    Пример создания:
        await create_or_update_with_on_conflict(session, Union, {}, dict(name='new', is_yellow=True), [Union.name])
    """
    stmt = insert(
        model
    ).values(
        update_kwargs | lookup_kwargs
    ).on_conflict_do_update(
        index_elements=unique_fields,
        set_=update_kwargs,
    ).returning(
        model,
    )
    instance = await session.scalar(stmt)
    await session.commit()

    return instance


async def create_or_update_with_session_get(session: 'AsyncSession',
                                            model: Type[MODEL_T] | str,
                                            data: dict[str, Any],
                                            ) -> MODEL_T:
    """
    Создает или обновляет запись модели в БД.
    """
    if isinstance(model, str):
        model = Base.get_model_by_name(model)

    pk = data.get(get_pk_name(model), None)
    if pk is None:  # создание новой записи.
        session.add(instance := model(**data))
    else:  # обновление уже существующей записи.
        instance = await session.get(model, pk, with_for_update=True)
        if instance is not None:
            for field, value in data.items():
                setattr(instance, field, value)
        else:
            raise ValueError(f'{str(model)} with id={pk} was not found in DB.')

    await session.commit()
    return instance
