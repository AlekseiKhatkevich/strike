import dataclasses

import strawberry
from sqlalchemy import func, select
from strawberry.types import Info
from graphql_related.types import Detention
from internal.typing_and_types import DataclassType
from models.detention import Detention as DetentionModel

__all__ = (
    'Query',
)


async def get_detentions(root: DataclassType, info: Info, name: str | None = None) -> list['Detention']:
    """
    Получение списка заключений для квери detentions.
    Name - имя заключенного.
    """
    session = info.context['session']
    stmt = select(DetentionModel).order_by(func.lower(DetentionModel.duration).desc())
    if name is not None:
        stmt = stmt.where(DetentionModel.name == name)
    data = await session.scalars(stmt)
    exc = {'jail'}
    f_names = [f.name for f in dataclasses.fields(Detention) if f.name not in exc]
    detentions = []
    for det in data:
        data = {f_name: getattr(det, f_name) for f_name in f_names}
        detentions.append(Detention(**data))
    return detentions


@strawberry.type
class Query:
    detentions: list[Detention] = strawberry.field(resolver=get_detentions)
