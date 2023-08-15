import datetime
import enum

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, Range, TSTZRANGE
from sqlalchemy.orm import Mapped, mapped_column
from serializers.proto.compiled.conflicts_pb2 import (Conflict as PBConflict,
                                                      ConflictTypes as PBConflictTypes)
from internal.database import Base
from internal.typing_and_types import BigIntType
from .annotations import BigIntPk
from .mixins import CreatedUpdatedMixin

__all__ = (
    'Conflict',
    'ConflictTypes',
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

    def to_protobuf(self):
        """

        """
        conflict_pb = PBConflict()
        for filed_name in conflict_pb.DESCRIPTOR.fields_by_name.keys():
            match filed_name:
                case 'duration':
                    conflict_pb.duration.lower.FromDatetime(self.duration.lower)
                    conflict_pb.duration.upper.FromDatetime(self.duration.upper)
                case 'type':
                    conflict_pb.type = getattr(PBConflictTypes, self.type.name)
                case _:
                    setattr(conflict_pb, filed_name, getattr(self, filed_name))

        return conflict_pb

