from typing import TYPE_CHECKING

from sqlalchemy import insert

from models import User

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
    async with session.begin():
        stmt = insert(User).values(
                name=user_data.name,
                email=user_data.email,
                hashed_password=user_data.password.get_secret_value(),
            )
        db_response = await session.execute(stmt)

        # noinspection PyUnresolvedReferences
        return db_response.inserted_primary_key[0]
