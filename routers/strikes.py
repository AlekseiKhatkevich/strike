from fastapi import APIRouter, Depends, status
from fastapi_pagination import LimitOffsetPage
from sqlalchemy import column

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete, get_collection_paginated
from crud.strikes import (
    create_strike,
    get_strikes, manage_group,
    manage_places,
    manage_users_involved,
)
from internal.dependencies import (
    GetParamsIdsDep, PaginParamsDep, PathIdDep,
    SessionDep,
    UserIdDep,
    jwt_authorize,
)
from serializers.strikes import (
    AddRemoveStrikeM2MObjectsSerializer,
    AddRemoveUsersInvolvedSerializer,
    StrikeInSerializer,
    StrikeOutSerializerFull,
    StrikeOutSerializerShort,
    StrikeUpdateInSerializer,
    StrikeWithAllRelatedSerializer, UsersInvolvedOutSerializer,
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


@router.patch('/{id}')
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


@router.post('/{id}/group')
async def manage_group_ep(_id: PathIdDep,
                          session: SessionDep,
                          m2m_ids: AddRemoveStrikeM2MObjectsSerializer,
                          ) -> list[int]:
    """
    ЭП создания / удаления м2м связи Stike в группы.
    """
    return await manage_group(session, _id, m2m_ids)


@router.post('/{id}/places')
async def manage_places_ep(_id: PathIdDep,
                           session: SessionDep,
                           m2m_ids: AddRemoveStrikeM2MObjectsSerializer,
                           ) -> set[int]:
    """
    ЭП создания / удаления м2м связи Stike с Place.
    """
    return await manage_places(session, _id, m2m_ids)


@router.post('/{id}/users_involved')
async def manage_users_involved_ep(_id: PathIdDep,
                                   session: SessionDep,
                                   m2m: AddRemoveUsersInvolvedSerializer,
                                   ) -> list[UsersInvolvedOutSerializer]:
    """
    ЭП создания / удаления м2м связи Stike с User.
    """
    # noinspection PyTypeChecker
    return await manage_users_involved(session, _id, m2m)


@router.get('/', response_model_by_alias=False)
async def get_strikes_ep(session: SessionDep,
                         params: PaginParamsDep,
                         ids: GetParamsIdsDep,
                         # ):
                        ) -> LimitOffsetPage[StrikeWithAllRelatedSerializer]:
    """

    """
    # флаг для показа только активных страйков
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#adding-criteria-to-loader-options
    col = await get_strikes(session, ids, params)
    out = LimitOffsetPage[StrikeWithAllRelatedSerializer]
    return out.create(col.items, params, total=col.total)
