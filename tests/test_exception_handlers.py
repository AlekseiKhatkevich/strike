import json

from fastapi import status

from main import invitation_token_exception_handler
from security.invitation import InvitationTokenDeclinedException


async def test_invitation_token_exception_handler():
    """
    Тест обработчика исключений InvitationTokenDeclinedException.
    """
    resp = await invitation_token_exception_handler(None, exc=InvitationTokenDeclinedException())

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert json.loads(resp.body)['detail'] == InvitationTokenDeclinedException.text
