import dataclasses
import datetime
from typing import NewType

import strawberry
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import Range

from models.detention import Jail as JailModel

__all__ = (
    'DurationType',
    'Jail',
    'Detention',
    'Strike',
)

from internal.database import async_session

DurationType = strawberry.scalar(
    NewType('DurationType', Range[datetime.datetime]),
    serialize=lambda v: jsonable_encoder(v),
    parse_value=lambda v: Range(*v),
    description='DateTime duration between 2 datetimes',
)


@strawberry.type
class Jail:
    """
    Крытая.
    """
    id: int
    name: str
    address: str
    region_id: str


@strawberry.type
class Detention:
    """
    Заключение в крытой.
    """
    id: int
    duration: DurationType
    name: str
    extra_personal_info: str | None
    needs_medical_attention: bool
    needs_lawyer: bool
    jail_id: int
    charge: str | None
    transferred_from_id: int | None
    relative_or_friend: str | None

    @strawberry.field
    async def jail(self) -> Jail:
        async with async_session() as session:
            j = await session.get(JailModel, self.jail_id)
            return Jail(
                id=j.id,
                name=j.name,
                address=j.address,
                region_id=j.region_id,
            )

    @classmethod
    def f_names(cls) -> list[str, ...]:
        exc = {'jail', }
        return [f.name for f in dataclasses.fields(cls) if f.name not in exc]


@strawberry.type
class Strike:
    """
    Забастовка.
    """
    id: int
    duration: DurationType
    planned_on_date: datetime.date | None
    goals: str
    results: str | None
    overall_num_of_employees_involved: int
    enterprise_id: int
    created_by_id: int
    union_in_charge_id: int | None
