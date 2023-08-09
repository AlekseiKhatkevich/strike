import datetime

import strawberry
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import Range, insert, TSTZRANGE
from strawberry.fastapi import GraphQLRouter
import dataclasses
from internal.database import async_session
from models.detention import Detention as DetentionModel, Jail as JailModel

__all__ = (
    'graphql_app',
)


async def get_detentions(root) -> list['Detention']:
    async with async_session() as session:
        data = await session.scalars(
            select(DetentionModel).order_by(func.lower(DetentionModel.duration).desc())
        )
        exc = {'duration', 'jail'}
        f_names = [f.name for f in dataclasses.fields(Detention) if f.name not in exc]
        detentions = []
        for det in data:
            data = {f_name: getattr(det, f_name) for f_name in f_names}
            data['duration'] = Duration(lower=det.duration.lower, upper=det.duration.upper)
            detentions.append(Detention(**data))
        return detentions


async def get_jail_for_detention(root):
    async with async_session() as session:
        j = await session.get(JailModel, root.jail_id)
        return Jail(
            id=j.id,
            name=j.name,
            address=j.address,
            region_id=j.region_id,
        )


@strawberry.type
class Duration:
    lower: datetime.datetime
    upper: datetime.datetime | None


@strawberry.type
class Jail:
    id: int
    name: str
    address: str
    region_id: str


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
    jail: Jail = strawberry.field(resolver=get_jail_for_detention)

    @classmethod
    def f_names(cls):
        exc = {'jail', }
        return [f.name for f in dataclasses.fields(cls) if f.name not in exc]


@strawberry.input
class ZKTransferInput:
    detention_id: int = strawberry.field(description='Who is transferred')
    jail: int = strawberry.field(description='Transfer poor motherfucker where exactly')
    transfer_dt: datetime.datetime = strawberry.field(description='Transfer datetime')
    detention_upper: datetime.datetime | None = strawberry.field(description='Extend cell time if needed.')


@strawberry.type
class Mutation:
    @strawberry.field
    async def zk_transfer(self, transfer: ZKTransferInput) -> Detention:
        async with async_session() as session:
            old_detention = await session.get(DetentionModel, transfer.detention_id)
            upper_detention_time = transfer.detention_upper or old_detention.duration.upper
            old_detention.duration = Range(old_detention.duration.lower, transfer.transfer_dt, bounds='()')

            await session.commit()

            new_detention = DetentionModel(
                duration=Range(transfer.transfer_dt, upper_detention_time, bounds='()'),
                name=old_detention.name,
                extra_personal_info=old_detention.extra_personal_info,
                needs_medical_attention=old_detention.needs_medical_attention,
                needs_lawyer=old_detention.needs_lawyer,
                jail_id=transfer.jail,
                charge=old_detention.charge,
                transferred_from_id=old_detention.id,
                relative_or_friend=old_detention.relative_or_friend,
            )
            session.add(new_detention)

            await session.commit()

            f_names = Detention.f_names()
            return Detention(**{f_name: getattr(new_detention, f_name) for f_name in f_names})

@strawberry.type
class Query:
    detentions: list[Detention] = strawberry.field(resolver=get_detentions)


schema = strawberry.Schema(Query, Mutation)

graphql_app = GraphQLRouter(schema)
