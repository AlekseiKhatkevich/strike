
from fastapi import APIRouter, Depends, status

from crud.strikes import create_strike
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
                           ):
    """


    """
    strike_data._created_by_id = user_id

    res = await create_strike(session, strike_data)
    # return res
    # return strike_data.dict()


