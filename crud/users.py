import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from crud.auth import check_invitation_token_used_already
from crud.helpers import commit_if_not_in_transaction
from models import User, UsedToken
from security.hashers import make_hash
from security.invitation import verify_invitation_token

if TYPE_CHECKING:
    from serializers.users import UserRegistrationSerializer
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'create_new_user',
    'get_user_by_id',
)


@commit_if_not_in_transaction
async def get_user_by_id(session, user_id):
    """

    """
    return session.scalar(
        select(User).where(User.id == user_id)
    )


async def create_new_user(session: 'AsyncSession', user_data: 'UserRegistrationSerializer') -> User:
    """
    Создание нового пользователя в БД.
    """
    await check_invitation_token_used_already(session, user_data.invitation_token.get_secret_value())
    decoded_token = verify_invitation_token(
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
    used_token = UsedToken(
        token=user_data.invitation_token.get_secret_value(),
        issued_at=datetime.datetime.fromtimestamp(decoded_token['iat']).astimezone(datetime.UTC),
    )

    user.used_token = used_token
    session.add(user)
    await session.commit()
    return user
