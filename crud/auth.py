from typing import TYPE_CHECKING

from sqlalchemy import select

from models import CommonPassword, UsedToken
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
    stmt = select(CommonPassword.id).where(CommonPassword.password == password).limit(1)
    password_exists = bool(await session.scalar(stmt))
    return password_exists


async def check_invitation_token_used_already(session: 'AsyncSession', token: str) -> None:
    """
    Проверка того был ли пригласительный токен уже использован.
    """
    stmt = select(UsedToken.id).filter_by(token=token).limit(1)
    was_used_before = bool(await session.scalar(stmt))
    if was_used_before:
        raise InvitationTokenDeclinedException()
