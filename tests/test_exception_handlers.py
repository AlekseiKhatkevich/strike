import json

import pytest
from fastapi import status

from main import invitation_token_exception_handler, model_does_not_exists_exception_handler
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
        ModelEntryDoesNotExistsInDbError(expected_error_message),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(resp.body)['detail'] == expected_error_message
