from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import undefer

from crud.helpers import exists_in_db, commit_if_not_in_transaction
from models import CommonPassword, UsedToken, User
from security import sensitive
from security.hashers import verify_hash
from security.invitation import InvitationTokenDeclinedException

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'check_password_commonness',
    'check_invitation_token_used_already',
    'authenticate_user',
)


async def check_password_commonness(session: 'AsyncSession',  password: str) -> bool:
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


@commit_if_not_in_transaction
async def authenticate_user(session: 'AsyncSession', name: str, password: str) -> bool | User:
    """
    Аутентифицирует юзера по пришедшему имени и паролю. Возвращает запись модели Юзера или False
    если она не была найдена или не была аутентифицирована.
    """
    user = await session.scalar(
        select(User).where(User.name == name, User.is_active == True).options(undefer(User.hashed_password))
    )
    if user is None:
        logger.info(f'User with name {name} does not exists or inactive.')
        return False

    password_ok = verify_hash(password, user.hashed_password)
    if not password_ok:
        logger.info(f'User with name {name} provided incorrect password')
        return False

    return user
