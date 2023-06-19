import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Text,
    ForeignKey,
    Enum,
    Column,
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.associationproxy import association_proxy
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
from models.mixins import UpdatedAtMixin, CreatedAtMixin
from models.validators import positive_integer_only

if TYPE_CHECKING:
    from .users import User

__all__ = (
    'Strike',
    'StrikeToUserAssociation',
    'UserRole',
    'StrikeToPlaceAssociation',
)


class UserRole(enum.Enum):
    """

    """
    employee = 'EMPLOYEE'
    union_member = 'UNION_MEMBER'
    observer = 'OBSERVER'
    guest = 'GUEST'
    spy = 'SPY'
    volunteer = 'VOLUNTEER'
    coordinator = 'COORDINATOR'


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
    role: Mapped[Enum | None] = mapped_column(
        Enum(UserRole, validate_strings=True),
    )
    user: Mapped['User'] = relationship(
        back_populates='strikes',
    )
    strike: Mapped['Strike'] = relationship(
        back_populates='users_involved',
    )

    def __repr__(self):
        return f'Strike intermediate table: strike {self.strike_id}, user {self.user_id}'


class StrikeToPlaceAssociation(CreatedAtMixin, Base):
    """

    """
    __tablename__ = 'strike_to_place_associations'

    strike_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('strikes.id', ondelete='CASCADE', ),
        primary_key=True,
    )
    place_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('places.id', ondelete='CASCADE', ),
        primary_key=True,
    )


class Strike(UpdatedAtMixin, Base):
    """
    Забастовка.
    """
    __tablename__ = 'strikes'

    id: Mapped[BigIntPk]
    duration = mapped_column(TSTZRANGE(), nullable=True)
    planned_on_date: Mapped[datetime.date | None]
    goals: Mapped[str] = mapped_column(Text())
    results: Mapped[str | None] = mapped_column(Text())
    overall_num_of_employees_involved: Mapped[int]
    enterprise_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('enterprises.id'),
    )
    # union_in_charge o2o
    # created_by_user
    # group m2m to itself

    # users_involved: Mapped[list['User']] = relationship(
    #     secondary=StrikeToUserAssociation.__table__,
    #     back_populates='strikes',
    #     passive_deletes=True,
    # )
    places: Mapped[list['Place']] = relationship(
        secondary='strike_to_place_associations',
        passive_deletes=True,
        back_populates='strikes',
    )
    users_involved: Mapped[list[StrikeToUserAssociation]] = relationship(
        back_populates='strike',
        passive_deletes=True,
    )
    enterprise: Mapped['Enterprise'] = relationship(back_populates='strikes')
    user_ids: AssociationProxy[list[int]] = association_proxy('users_involved', 'user_id')

    __table_args__ = (
        CheckConstraint(
            r'overall_num_of_employees_involved >= 1',
            name='overall_num_of_employees_involved_positive',
        ),
        CheckConstraint(
            func.num_nonnulls("duration", "planned_on_date") >= 1,
            name='one_of_dates_is_not_null',
        ),
        ExcludeConstraint(
            (Column('duration'), '&&'),
            (Column('enterprise_id'), '='),
            name='duration_enterprise_exc_constraint',
        ),
    )

    def __repr__(self):
        return f'Strike {self.id} on enterprise {self.enterprise_id}'

    @validates('overall_num_of_employees_involved')
    def validate_overall_num_of_employees_involved(self, field, value):
        """

        """
        return positive_integer_only(field, value)
