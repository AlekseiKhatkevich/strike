from fastapi import APIRouter, Depends, status
from sqlalchemy import column

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from crud.strikes import create_strike
from internal.dependencies import PathIdDep, SessionDep, UserIdDep, jwt_authorize
from serializers.strikes import (
    StrikeInSerializer,
    StrikeOutSerializerFull,
    StrikeOutSerializerShort, StrikeUpdateInSerializer,
)

__all__ = (
    'router',
)

router = APIRouter(tags=['strike'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_strike_ep(session: SessionDep,
                           user_id: UserIdDep,
                           strike_data: StrikeInSerializer,
                           ) -> StrikeOutSerializerFull:
    """
    Эндпоинт создания записи Strike и ассоциированных с ней моделей.
    """
    strike_data._created_by_id = user_id
    strike_instance = await create_strike(session, strike_data)

    return strike_instance


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_strike_ep(_id: PathIdDep, session: SessionDep):
    """
    Эндпоинт удаления Enterprise.
    """
    await delete_via_sql_delete(session, 'Strike', column('id') == _id)


@router.patch('/{id}',)
async def update_strike_ep(_id: PathIdDep,
                           session: SessionDep,
                           strike_data: StrikeUpdateInSerializer,
                           ) -> StrikeOutSerializerShort:
    """
    Обновление записи Strike по ее id.
    """
    strike_data_dict = strike_data.model_dump(exclude_unset=True)
    strike_data_dict['id'] = _id
    updated_strike = await create_or_update_with_session_get(
        session,
        model='Strike',
        data=strike_data_dict,
    )
    return updated_strike
