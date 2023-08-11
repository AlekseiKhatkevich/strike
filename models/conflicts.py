import datetime
import enum

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, Range, TSTZRANGE
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import Base
from internal.typing_and_types import BigIntType
from .annotations import BigIntPk
from .mixins import CreatedUpdatedMixin

__all__ = (
    'Conflict',
)


class ConflictTypes(enum.StrEnum):
    """
    Типы конфликтов.
    """
    PAYMENT = 'payment'
    LAYOFF = 'layoff'
    LIQUIDATION = 'liquidation'
    OTHER = 'other'
    DISMISSAL = 'dismissal'
    MANAGEMENT_POLITICS = 'management_politics'
    WORK_CONDITIONS = 'work_conditions'
    LABOR_HOURS = 'labor_hours'
    COLLECTIVE_AGREEMENT = 'collective_agreement'
    PAYMENT_DELAY = 'payment_delay'
    LABOUR_RIGHTS = 'labour_rights'


class Conflict(CreatedUpdatedMixin, Base):
    """
    Трудовой конфликт.
    """
    __tablename__ = 'conflicts'

    id: Mapped[BigIntPk]
    type: Mapped[enum.Enum] = mapped_column(
        ENUM(ConflictTypes, validate_strings=True)
    )
    duration: Mapped[Range[datetime.datetime]] = mapped_column(
        TSTZRANGE(), index=True,
    )
    enterprise_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('enterprises.id', ondelete='CASCADE')
    )
    description: Mapped[str]
    results: Mapped[str | None]
    success_rate: Mapped[float | None] = mapped_column()

    __table_args__ = (
        CheckConstraint((success_rate >= 0) & (success_rate <= 1), name='success_rate_between_0_1'),
    )

    def __repr__(self):
        return f'{self.type} conflict in company {self.enterprise_id}'

