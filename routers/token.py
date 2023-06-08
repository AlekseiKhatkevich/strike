from typing import Annotated, TYPE_CHECKING
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from crud.auth import authenticate_user
from internal.dependencies import SessionDep
from security.jwt import generate_jwt_token

if TYPE_CHECKING:
    from models import User

__all__ = (
    'router',
)


router = APIRouter(tags=['token'])


async def authenticate_user_by_creds(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    """

    :param form_data:
    :param session:
    :param name:
    :param password:
    :return:
    """
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
    return user


@router.post('/')
async def obtain_token(user: Annotated['User', Depends(authenticate_user_by_creds)]) -> dict:
    """

    """
    return {'access_token': generate_jwt_token(user.id), 'token_type': 'bearer'}
