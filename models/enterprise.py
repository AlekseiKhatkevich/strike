from sqlalchemy import String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk
from models.mixins import UpdatedAtMixin


__all__ = (
    'Enterprise',
)


class Enterprise(UpdatedAtMixin, Base):
    """

    """
    __tablename__ = 'enterprises'

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(
        String(256),
    )
    region_name: Mapped[BigIntType] = mapped_column(
        ForeignKey('regions.name', ondelete='PROTECT',),
    )
    place: Mapped[str] = mapped_column(
        Text(collation=RU_RU_CE_COLLATION_NAME),
    )
    address: Mapped[str] = mapped_column(
        String(512),
    )
    field_of_activity: Mapped[str | None] = mapped_column(
        String(256),
    )

    __table_args__ = (
        UniqueConstraint(name, region_name, place),
    )
