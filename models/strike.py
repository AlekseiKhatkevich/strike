import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.orm import (
    validates,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk
from models.mixins import UpdatedAtMixin
from models.validators import positive_integer_only

if TYPE_CHECKING:
    from .users import User

__all__ = (
    'Strike',
    'StrikeToUserAssociation',
)


class StrikeToUserAssociation(Base):
    """

    """
    __tablename__ = 'strike_to_user_associations'

    strike_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('strikes.id', ondelete='CASCADE',),
        primary_key=True,
    )
    user_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE',),
        primary_key=True,
    )


class Strike(UpdatedAtMixin, Base):
    """
    Забастовка.
    """
    __tablename__ = 'strikes'

    id: Mapped[BigIntPk]
    # started_at: Mapped[datetime.datetime | None]
    # finished_at: Mapped[datetime.datetime | None]
    duration = mapped_column(TSTZRANGE(), nullable=True)
    planned_on_date: Mapped[datetime.date | None]
    # enterprise o2o
    goals: Mapped[str] = mapped_column(Text())
    results: Mapped[str | None] = mapped_column(Text())
    overall_num_of_employees_involved: Mapped[int]
    # places m2m
    # union_in_charge o2o
    # created_by_user

    users_involved: Mapped[list['User']] = relationship(
        secondary=StrikeToUserAssociation.__table__,
        back_populates='strikes',
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            r'overall_num_of_employees_involved >= 1',
            name='overall_num_of_employees_involved_positive',
        ),
        CheckConstraint(
            func.num_nonnulls("duration", "planned_on_date") >= 1,
            name='one_of_dates_is_not_null',
        ),
    )

    def __repr__(self):
        return f'Strike {self.id} on enterprise %ENTERPRISE PLACEHOLDER%'

    @validates('overall_num_of_employees_involved')
    def validate_overall_num_of_employees_involved(self, field, value):
        """

        """
        return positive_integer_only(field, value)
