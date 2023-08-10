import strawberry
from sqlalchemy.dialects.postgresql import Range
from strawberry.types import Info

from graphql_related.inputs import ZKTransferInput
from graphql_related.types import Detention
from models.detention import Detention as DetentionModel

__all__ = (
    'Mutation',
)


@strawberry.type
class Mutation:
    @strawberry.field
    async def zk_transfer(self, info: Info, transfer: ZKTransferInput) -> Detention:
        """
        Перевод зк из одной крытой в другую.
        """
        session = info.context['session']
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

