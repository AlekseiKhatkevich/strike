from fastapi import APIRouter, status, HTTPException
from sqlalchemy import exc as so_exc

from dependencies import SessionDep
from serializers.crud.users import create_new_user
from serializers.users import UserRegistrationSerializer

__all__ = (
    'router',
)


router = APIRouter(tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def register_new_user(session: SessionDep, user_data: UserRegistrationSerializer) -> dict[str, int]:
    """
    """
    try:
        created_user_id = await create_new_user(session, user_data)
    except so_exc.IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this name or email already exists',
        ) from err

    return {'id': created_user_id}


@router.get('/ping/')
async def ping():
    return {"ping": "pong!"}
