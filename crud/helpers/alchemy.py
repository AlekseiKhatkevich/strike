import os
import re
from functools import cache, wraps
from typing import Any, Callable, TYPE_CHECKING, Type, TypeVar

from fastapi import HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, exc as sa_exc, inspect, select
from sqlalchemy.dialects.postgresql import insert

from internal.database import Base
from models.exceptions import ModelEntryDoesNotExistsInDbError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.elements import OperatorExpression
    from fastapi_pagination.bases import AbstractParams

__all__ = (
    'exists_in_db',
    'commit_if_not_in_transaction',
    'create_or_update_with_on_conflict',
    'create_or_update_with_session_get',
    'delete_via_sql_delete',
    'is_instance_in_db',
    'get_collection_paginated',
    'get_id_from_integrity_error',
    'flush_and_raise',
    'get_text_from_integrity_error',
    'get_constr_name_from_integrity_error',
)

MODEL_T = TypeVar('MODEL_T', bound='Base')
ID_T = TypeVar('ID_T')


@cache
def get_pk_name(model: 'Base') -> str:
    """
    Название первичного ключа модели.
    """
    pk_inst = inspect(model).primary_key
    return pk_inst[0].name


def model_from_string(func: Callable) -> Callable:
    """
    Позволяет передавать модель как строку, т.е. ее название.
    """
    @wraps(func)
    async def wrapper(session: 'AsyncSession', model: Type[MODEL_T] | str, *args, **kwargs):
        if isinstance(model, str):
            model = Base.get_model_by_name(model)
        return await func(session, model, *args, **kwargs)

    return wrapper


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


@commit_if_not_in_transaction
async def is_instance_in_db(session: 'AsyncSession', instance: Base) -> bool:
    """
    Есть ли этот инстанс в БД или нет?
    """
    cls = instance.__class__
    pk_name = get_pk_name(cls)
    cls_pk = getattr(cls, pk_name)
    instance_pk = getattr(instance, pk_name)

    # noinspection PyTypeChecker
    return await session.scalar(
        select(cls_pk).where(cls_pk == instance_pk).limit(1)
    ) is not None


@model_from_string
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


@model_from_string
async def create_or_update_with_session_get(session: 'AsyncSession',
                                            model: Type[MODEL_T] | str,
                                            data: dict[str, Any],
                                            *,
                                            load_expired: bool = False,
                                            error_message: str = None,
                                            ) -> MODEL_T:
    """
    Создает или обновляет запись модели в БД.
    """
    pk = data.get(get_pk_name(model), None)
    if pk is None:  # создание новой записи.
        session.add(instance := model(**data))
    else:  # обновление уже существующей записи.
        instance = await session.get(model, pk, with_for_update=True)
        if instance is not None:
            for field, value in data.items():
                setattr(instance, field, value)
        else:
            raise ModelEntryDoesNotExistsInDbError(
                error_message or f'{model.__name__} with id={pk} was not found in DB.',
                report=True,
            )

    await session.commit()
    if load_expired:
        await session.refresh(instance, inspect(instance).expired_attributes)
    return instance


@model_from_string
async def delete_via_sql_delete(session: 'AsyncSession',
                                model: Type[MODEL_T] | str,
                                condition: 'OperatorExpression',
                                ) -> list[ID_T, ...]:
    """
    Удаление записей модели по каким то условиям. Возвращает список удаленных id.
    """
    result = await session.scalars(
        delete(model).where(condition).returning(getattr(model, get_pk_name(model)))
    )
    await session.commit()
    # noinspection PyTypeChecker
    return result.all()


@model_from_string
@commit_if_not_in_transaction
async def get_collection_paginated(session: 'AsyncSession',
                                   model: Type[MODEL_T] | str,
                                   ids: list[int],
                                   params: 'AbstractParams',
                                   ) -> list[MODEL_T]:
    """
    Отдает 1 или несколько записей модели с пагинацией.
    """
    pk_name = get_pk_name(model)
    pk = getattr(model, pk_name)
    stmt = select(model).order_by(pk_name)

    if ids:
        stmt = stmt.where(pk.in_(ids))

    return await paginate(session, stmt, params)


def get_text_from_integrity_error(exc: sa_exc.IntegrityError) -> str:
    """
    Получает текст исключения из IntegrityError.
    Пример:  DETAIL:  Ключ (strike_right_id)=(277) отсутствует в таблице "strikes".
    """
    return exc.orig.args[0].split(os.linesep)[-1]


def get_id_from_integrity_error(exc: sa_exc.IntegrityError) -> str:
    """
    Получает id из текста сообщения из исключения IntegrityError. Пример сообщения ниже:
    DETAIL:  Ключ (strike_right_id)=(277) отсутствует в таблице "strikes".
    """
    return re.search(r'=\((?P<id>[\w ]+?)\)', get_text_from_integrity_error(exc)).group('id')


def get_constr_name_from_integrity_error(exc: sa_exc.IntegrityError) -> str:
    """
    """
    return re.search(r'"(?P<name>\w+)"\nDETAIL', exc.orig.args[0]).group('name')


async def flush_and_raise(session: 'AsyncSession', error_message: str) -> None:
    """
    Делает flush сессии и в случае возбуждения исключения на стороне БД
    возбуждает исключение HTTPException с переданным в аргументах сообщением.
    """
    try:
        await session.flush()
    except sa_exc.IntegrityError as err:
        _id = get_id_from_integrity_error(err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message.format(id=_id),
        ) from err
