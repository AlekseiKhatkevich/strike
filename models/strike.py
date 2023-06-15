import datetime

from sqlalchemy import (
    CheckConstraint,
    Text,
)
from sqlalchemy.orm import (
    validates,
    Mapped,
    mapped_column,
)
from sqlalchemy.sql import func

from internal.database import Base
from models.annotations import BigIntPk
from models.mixins import UpdatedAtMixin

__all__ = (
    'Strike',
)

from models.validators import positive_integer_only


class Strike(UpdatedAtMixin, Base):
    """
    Забастовка.
    """
    __tablename__ = 'strikes'

    id: Mapped[BigIntPk]
    # users_involved m2m
    started_at: Mapped[datetime.datetime | None]
    finished_at: Mapped[datetime.datetime | None]
    planned_on_date: Mapped[datetime.date | None]
    # enterprise o2o
    goals: Mapped[str] = mapped_column(Text())
    results: Mapped[str | None] = mapped_column(Text())
    overall_num_of_employees_involved: Mapped[int]
    # places m2m
    # union_in_charge o2o
    # created_by_user

    __table_args__ = (
        CheckConstraint(
            r'overall_num_of_employees_involved >= 1',
            name='overall_num_of_employees_involved_positive',
        ),
        CheckConstraint(
            func.num_nonnulls("started_at", "finished_at", "planned_on_date") >= 1,
            name='one_of_dates_is_not_null',
        ),
        CheckConstraint(
            r'finished_at > started_at',
            name='finished_gt_started',
        ),
    )

    def __str__(self):
        return f'Strike {self.id} on enterprise %ENTERPRISE PLACEHOLDER%'

    __repr__ = __str__

    @validates('overall_num_of_employees_involved')
    def validate_overall_num_of_employees_involved(self, field, value):
        """

        """
        return positive_integer_only(field, value)
