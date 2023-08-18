from typing import Sequence, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Range

from models import Conflict

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from serializers.conflicts import ConflictsRequestedConditionsSerializer

__all__ = (
    'list_conflicts',
)


async def list_conflicts(
        session: 'AsyncSession',
        conditions: 'ConflictsRequestedConditionsSerializer',
) -> Sequence[Conflict]:
    """
    Получает из БД список конфликтов по переданным в "conditions" условиям фильтрации.
    """
    stmt = select(Conflict).order_by('id')

    if ids := conditions.ids:
        stmt = stmt.where(Conflict.id.in_(ids))
    if types := conditions.types:
        stmt = stmt.where(Conflict.type.in_(types))
    if not (duration := conditions.duration).is_empty():
        duration = Range(duration.lower, duration.upper)
        stmt = stmt.where(Conflict.duration.op('<@')(duration))
    if enterprise_ids := conditions.enterprise_ids:
        stmt = stmt.where(Conflict.enterprise_id.in_(enterprise_ids))
    if success_rate := conditions.success_rate.condition:
        gte, lte = success_rate
        stmt = stmt.where(Conflict.success_rate >= gte, Conflict.success_rate <= lte)

    conflicts = await session.scalars(stmt)

    return conflicts.all()
