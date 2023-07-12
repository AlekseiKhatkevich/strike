from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, query_expression, relationship

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk
from models.mixins import CreatedUpdatedMixin

__all__ = (
    'Enterprise',
)


class Enterprise(CreatedUpdatedMixin, Base):
    """
    Модель компании.
    """
    __tablename__ = 'enterprises'

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(
        String(256),
    )
    region_name: Mapped[BigIntType] = mapped_column(
        ForeignKey('regions.name', ondelete='RESTRICT', onupdate='CASCADE',),
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
    region: Mapped['Region'] = relationship(innerjoin=True)
    strikes: Mapped[list['Strike']] = relationship(back_populates='enterprise')
    strikes_count: Mapped[int] = query_expression()

    __table_args__ = (
        UniqueConstraint(name, region_name, place),
    )

    def __repr__(self):
        return f'Enterprise "{self.name}" in region "{self.region_name}"'
