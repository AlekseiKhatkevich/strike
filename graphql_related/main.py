import datetime

import strawberry
from sqlalchemy import func, select
from strawberry.fastapi import GraphQLRouter
import dataclasses
from internal.database import async_session
from models.detention import Detention as DetentionModel

__all__ = (
    'graphql_app',
)


async def get_detentions():
    async with async_session() as session:
        data = await session.scalars(
            select(DetentionModel).order_by(func.lower(DetentionModel.duration).desc())
        )
        f_names = [f.name for f in dataclasses.fields(Detention)]
        detentions = []
        for det in data:
            data = {f_name: getattr(det, f_name) for f_name in f_names}
            data['duration'] = Duration(lower=det.duration.lower, upper=det.duration.upper)
            detentions.append(Detention(**data))
        return detentions


@strawberry.type
class Duration:
    lower: datetime.datetime
    upper: datetime.datetime | None


@strawberry.type
class Detention:
    id: int
    duration: Duration
    name: str
    extra_personal_info: str | None
    needs_medical_attention: bool
    needs_lawyer: bool
    jail_id: int
    charge: str | None
    transferred_from_id: int | None
    relative_or_friend: str | None


@strawberry.type
class Query:
    detentions: list[Detention] = strawberry.field(resolver=get_detentions)


schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema)
