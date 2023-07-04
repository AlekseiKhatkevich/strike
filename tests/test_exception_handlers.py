import json
import os

import pytest
from fastapi import status
from sqlalchemy.exc import IntegrityError

from main import invitation_token_exception_handler, model_does_not_exists_exception_handler, integrity_error_handler
from models.exceptions import ModelEntryDoesNotExistsInDbError
from security.invitation import InvitationTokenDeclinedException


@pytest.mark.no_db_calls
async def test_invitation_token_exception_handler():
    """
    Тест обработчика исключений InvitationTokenDeclinedException.
    """
    resp = await invitation_token_exception_handler(None, exc=InvitationTokenDeclinedException())

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert json.loads(resp.body)['detail'] == InvitationTokenDeclinedException.text


@pytest.mark.no_db_calls
async def test_model_does_not_exists_exception_handler():
    """
    Тест обработчика исключений ModelEntryDoesNotExistsInDbError.
    """
    expected_error_message = 'test'
    resp = await model_does_not_exists_exception_handler(
        None,
        ModelEntryDoesNotExistsInDbError(expected_error_message, True),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(resp.body)['detail'] == expected_error_message


class OrigExc(BaseException):
    """То, что оборачивает IntegrityError"""
    def __init__(self, pgcode) -> None:
        self.pgcode = pgcode

    expected_error_message = 'test'
    orig_message = 'test_orig_message'
    args = [f'bullshit {os.linesep}{orig_message}', ...]


async def test_integrity_error_handler_unique():
    """
    В случае получения IntegrityError в ее варианте нарушения уникальности
    отдает 400 й респонс.
    """
    orig_exc = OrigExc(pgcode='23505')
    exc = IntegrityError(orig_exc.expected_error_message, orig=orig_exc, params=None)

    resp = await integrity_error_handler(None, exc)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(resp.body)['detail'] == f'Uniqueness violation {orig_exc.orig_message}'


async def test_integrity_error_handler_rest():
    """
    В остальных случаях просто ререйзим полученное исключение.
    """
    orig_exc = OrigExc(pgcode='228')
    exc = IntegrityError(orig_exc.expected_error_message, orig=orig_exc, params=None)

    with pytest.raises(IntegrityError):
        await integrity_error_handler(None, exc)
