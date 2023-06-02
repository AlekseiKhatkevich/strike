from typing import TYPE_CHECKING

from sqlalchemy import select

from models import User, CommonPassword
from security.hashers import make_hash
from security.invitation import verify_invitation_token

if TYPE_CHECKING:
    from serializers.users import UserRegistrationSerializer
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'create_new_user',
    'check_password_commonness',
)


async def create_new_user(session: 'AsyncSession', user_data: 'UserRegistrationSerializer') -> User:
    """
    Создание нового пользователя в БД.
    """
    verify_invitation_token(
        token=user_data.invitation_token,
        username=user_data.name,
        password=user_data.invitation_password,
    )
    hashed_password = make_hash(user_data.password.get_secret_value())

    user = User(
                name=user_data.name,
                email=user_data.email,
                hashed_password=hashed_password,
            )
    async with session.begin():
        session.add(user)
    return user


async def check_password_commonness(session,  password) -> bool:
    """
    """
    stmt = select(CommonPassword.id).where(CommonPassword.password == password).limit(1)
    password_exists = bool(await session.scalar(stmt))
    return password_exists


