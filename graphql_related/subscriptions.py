import asyncio
import datetime
from typing import AsyncGenerator

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from graphql_related.helpers import type_from_model_instance
from graphql_related.types import Strike
from internal.constants import WS_NEW_STRIKES_TIME_PERIOD
from internal.database import async_session
from models.strike import Strike as StrikeModel

__all__ = (
    'Subscription',
)


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def new_strikes(self, info: Info, gt_dt: datetime.datetime) -> AsyncGenerator[Strike, None]:
        """
        Список страйков созданных после какого то переданного дейттайма.
        """
        max_dt = gt_dt
        session = info.context['session']
        while True:
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
