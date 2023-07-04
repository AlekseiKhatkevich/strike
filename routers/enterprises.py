from fastapi import APIRouter, Depends, status
from internal.dependencies import SessionDep, jwt_authorize


__all__ = (
    'router',
)


router = APIRouter(tags=['enterprises'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/')
async def create_or_update_enterprise_ep(session: SessionDep, enterprise_data):
    """

    """