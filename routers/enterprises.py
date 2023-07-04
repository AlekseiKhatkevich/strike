from fastapi import APIRouter, Depends, status

from crud.helpers import create_or_update_with_session_get
from internal.dependencies import SessionDep, jwt_authorize
from serializers.enterprises import EnterpriseInSerializer, EnterpriseOutSerializer

__all__ = (
    'router',
)


router = APIRouter(tags=['enterprises'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/')
async def create_or_update_enterprise_ep(session: SessionDep,
                                         enterprise_data: EnterpriseInSerializer,
                                         ) -> EnterpriseOutSerializer:
    """
    Создание / обновление записи модели Enterprise в БД.
    """
    return await create_or_update_with_session_get(
        session,
        'Enterprise',
        enterprise_data.dict(exclude_unset=True),
    )
