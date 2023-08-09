import asyncio
import dataclasses
import datetime
from typing import AsyncGenerator

import strawberry
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import Range
from strawberry.fastapi import GraphQLRouter

from internal.constants import WS_NEW_STRIKES_TIME_PERIOD
from internal.database import async_session
from models.detention import Detention as DetentionModel, Jail as JailModel
from models.strike import Strike as StrikeModel

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


def type_from_model_instance(strawberry_type, so_instance):
    f_names = [f.name for f in dataclasses.fields(strawberry_type)]
    return strawberry_type(**{f_name: getattr(so_instance, f_name) for f_name in f_names})


@strawberry.type
class Strike:
    id: int
    duration: Duration
    planned_on_date: datetime.date | None
    goals: str
    results: str | None
    overall_num_of_employees_involved: int
    enterprise_id: int
    created_by_id: int
    union_in_charge_id: int | None


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
            old_detention = await session.get(DetentionModel, transfer.detention_id, with_for_update=True)
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
class Subscription:
    @strawberry.subscription
    async def new_strikes(self, gt_dt: datetime.datetime) -> AsyncGenerator[Strike, None]:
        max_dt = gt_dt
        while True:
            async with async_session() as session:
                scalar_res = await session.scalars(
                    select(
                        StrikeModel
                    ).where(
                        StrikeModel.created_at > max_dt
                    ).order_by(
                        StrikeModel.created_at.desc()
                    )
                )
            new_strikes = scalar_res.all()
            if new_strikes:
                max_dt = max(new_strikes, key=lambda s: s.created_at).created_at
                for strike in new_strikes:
                    yield type_from_model_instance(Strike, strike)

            await asyncio.sleep(WS_NEW_STRIKES_TIME_PERIOD)


@strawberry.type
class Query:
    detentions: list[Detention] = strawberry.field(resolver=get_detentions)


schema = strawberry.Schema(Query, Mutation, subscription=Subscription)

graphql_app = GraphQLRouter(schema)
