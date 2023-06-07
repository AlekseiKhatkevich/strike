from typing import TYPE_CHECKING

from loguru import logger
from crud.helpers import exists_in_db
from models import CommonPassword, UsedToken
from security import sensitive
from security.invitation import InvitationTokenDeclinedException

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'check_password_commonness',
    'check_invitation_token_used_already',
)


async def check_password_commonness(session: 'AsyncSession',  password) -> bool:
    """
    Проверка пароля по базе распространенных паролей.
    """
    return await exists_in_db(session, CommonPassword, CommonPassword.password == password)


async def check_invitation_token_used_already(session: 'AsyncSession', token: str) -> None:
    """
    Проверка того был ли пригласительный токен уже использован.
    """
    was_used_before = await exists_in_db(session, UsedToken, UsedToken.token == token)
    if was_used_before:
        logger.info(f'Invitation token {sensitive(token)} has been already used.')
        raise InvitationTokenDeclinedException()
