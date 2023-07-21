from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from crud.helpers import (
    create_or_update_with_session_get,
    delete_via_sql_delete,
    exists_in_db,
)
from crud.users import delete_user
from internal.model_logging import _write_log_to_db, create_log
from models import CRUDLog, CRUDTypes, Union


@pytest.fixture
def log_writer() -> AsyncMock:
    """
    Патчим ф-цию _write_log_to_db.
    """
    with patch('internal.model_logging._write_log_to_db') as log_writer:
        yield log_writer


@pytest.fixture
def session_with_user_info(db_session, user_in_db) -> AsyncSession:
    """
    Добавляем в сессию инфу о текущем пользователе.
    """
    db_session.info['current_user_id'] = user_in_db.id
    return db_session


async def test_create_log_create(session_with_user_info, union_factory, log_writer):
    """
    Позитивный тест декоратора create_log. Случай с созданием инстанса через сессию.
    """
    decorated = create_log(create_or_update_with_session_get)
    union_data = union_factory.stub().__dict__

    instance = await decorated(session_with_user_info, model=Union, data=union_data)

    log_writer.assert_called_once_with(
            instance,
            session_with_user_info.info['current_user_id'],
            CRUDTypes.create,
            None,
        )


async def test_create_log_update(session_with_user_info, union, log_writer, faker):
    """
    Позитивный тест декоратора create_log. Случай с обновлением инстанса через сессию.
    """
    decorated = create_log(create_or_update_with_session_get)
    union_data = dict(name=faker.company(), id=union.id)

    instance = await decorated(session_with_user_info, model=Union, data=union_data)

    log_writer.assert_called_once_with(
        instance,
        session_with_user_info.info['current_user_id'],
        CRUDTypes.update,
        Union,
    )


async def test_create_log_SQLdelete(session_with_user_info, union, log_writer):
    """
    Позитивный тест декоратора create_log. Случай с удалением инстанса ч/з SQL DELETE.
    """
    decorated = create_log(delete_via_sql_delete)

    ids = await decorated(session_with_user_info, Union, Union.id == union.id)

    log_writer.assert_called_once_with(
        ids,
        session_with_user_info.info['current_user_id'],
        CRUDTypes.delete,
        Union,
    )


async def test_create_log_session_delete(session_with_user_info, user_in_db, log_writer):
    """
    Позитивный тест декоратора create_log. Случай с удалением инстанса через сессию.
    """
    decorated = create_log(delete_user)

    instance = await decorated(session_with_user_info, user_in_db)

    log_writer.assert_called_once_with(
        instance,
        session_with_user_info.info['current_user_id'],
        CRUDTypes.delete,
        None,
    )


async def test_write_log_to_db_with_instance(union, user_in_db, db_session):
    """
    Позитивный тест ф-ции _write_log_to_db. Когда есть инстанс полученный от
    декорируемой ф-ции.
    """
    await _write_log_to_db(union, user_in_db.id, CRUDTypes.create, session=db_session)

    assert await exists_in_db(
        db_session,
        CRUDLog,
        (CRUDLog.object_type == Union.__name__) &
        (CRUDLog.object_id == union.id) &
        (CRUDLog.action == CRUDTypes.create) &
        (CRUDLog.user_id == user_in_db.id) &
        (CRUDLog.operation_ts != None)
    )


async def test_write_log_to_db_without_instance(union, user_in_db, db_session):
    """
    Позитивный тест ф-ции _write_log_to_db. Случай когда декорируемая ф-ция отдает набор id.
    """
    await _write_log_to_db([union.id], user_in_db.id, CRUDTypes.delete, model=Union, session=db_session)

    assert await exists_in_db(
        db_session,
        CRUDLog,
        (CRUDLog.object_type == Union.__name__) &
        (CRUDLog.object_id == union.id) &
        (CRUDLog.action == CRUDTypes.delete) &
        (CRUDLog.user_id == user_in_db.id) &
        (CRUDLog.operation_ts != None)
    )
