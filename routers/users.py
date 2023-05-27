from fastapi import APIRouter, status

from database import async_session
from models import User
from serializers import UserRegistrationSerializer
from sqlalchemy import insert

__all__ = (
    'router',
)

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def register_new_user(user_data: UserRegistrationSerializer) -> dict[str, int]:
    """
    """
    async with async_session() as session:
        stmt = insert(User).values(
            name=user_data.name,
            email=user_data.email,
            hashed_password=user_data.password.get_secret_value(),
        )
        db_response = await session.execute(stmt)
        await session.commit()

    return {'id': db_response.inserted_primary_key[0]}

# todo валидация, перенос круда, сессия в депенденсиес, подтсвержение токена инвайта