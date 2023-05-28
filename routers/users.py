from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from serializers.users import UserRegistrationSerializer

__all__ = (
    'router',
)

from serializers.crud.users import create_new_user

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def register_new_user(session: Annotated[AsyncSession, Depends(get_session)], user_data: UserRegistrationSerializer) -> dict[str, int]:
    """
    """
    created_user_id = await create_new_user(session, user_data)

    return {'id': created_user_id}

# todo валидация, перенос круда, сессия в депенденсиес, подтсвержение токена инвайта