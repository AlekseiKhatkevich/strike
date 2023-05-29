from typing import TYPE_CHECKING

from sqlalchemy import insert

from models import User
from security.hashers import make_hash
from security.invitation import verify_invitation_token

if TYPE_CHECKING:
    from serializers.users import UserRegistrationSerializer
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'create_new_user',
)


async def create_new_user(session: 'AsyncSession', user_data: 'UserRegistrationSerializer') -> int:
    """
    :param session:
    :param user_data:
    :return:
    """
    verify_invitation_token(
        token=user_data.invitation_token,
        username=user_data.name,
        password=user_data.invitation_password,
    )
    hashed_password = make_hash(user_data.password.get_secret_value())

    async with session.begin():
        stmt = insert(User).values(
                name=user_data.name,
                email=user_data.email,
                hashed_password=hashed_password,
            )
        db_response = await session.execute(stmt)

        # noinspection PyUnresolvedReferences
        return db_response.inserted_primary_key[0]
