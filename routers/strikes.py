
from fastapi import APIRouter, Depends, status

from internal.dependencies import SessionDep, UserIdDep, jwt_authorize

__all__ = (
    'router',
)

from serializers.strikes import StrikeInSerializer

router = APIRouter(tags=['strike'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_strike_ep(session: SessionDep,
                           user_id: UserIdDep,
                           strike_data: StrikeInSerializer,
                           ) :
    """


    """
    return strike_data.dict()


