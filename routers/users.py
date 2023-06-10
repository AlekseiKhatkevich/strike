from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Depends,
)
from loguru import logger
from sqlalchemy import exc as so_exc

from config import settings
from crud.users import create_new_user
from internal.dependencies import SessionDep, jwt_authorize
from internal.ratelimit import limiter
from serializers.users import UserRegistrationSerializer

__all__ = (
    'router',
    'router_without_jwt',
)

router = APIRouter(tags=['users'], dependencies=[Depends(jwt_authorize)])
router_without_jwt = APIRouter(tags=['users'])


@router_without_jwt.post('/', status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.obtain_jwt_token_ratelimit)
async def register_new_user(session: SessionDep,
                            user_data: UserRegistrationSerializer,
                            request: Request,
                            ) -> dict[str, int]:
    """
    Создание пользователя.
    """
    try:
        created_user = await create_new_user(session, user_data)
    except so_exc.IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this name or email already exists',
        ) from err

    return {'id': created_user.id}


@router.get('/ping/')
async def ping(request: Request):
    logger.warning("some warnings")
    return request.state.user_id
