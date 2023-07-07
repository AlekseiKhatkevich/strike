from fastapi import APIRouter, Depends, status

from crud.strikes import create_strike
from internal.dependencies import SessionDep, UserIdDep, jwt_authorize
from serializers.strikes import StrikeInSerializer, StrikeOutSerializer

__all__ = (
    'router',
)

router = APIRouter(tags=['strike'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_strike_ep(session: SessionDep,
                           user_id: UserIdDep,
                           strike_data: StrikeInSerializer,
                           ) -> StrikeOutSerializer:
    """


    """
    strike_data._created_by_id = user_id

    strike_instance = await create_strike(session, strike_data)
    return strike_instance
