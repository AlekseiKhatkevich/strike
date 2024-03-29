import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ColumnElement,
    Text,
    ForeignKey,
    Enum,
    Column,
    UniqueConstraint,
    type_coerce,
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint, Range
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    query_expression,
    validates,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk
from models.mixins import CreatedUpdatedMixin, CreatedAtMixin
from models.validators import positive_integer_only

if TYPE_CHECKING:
    from .users import User

__all__ = (
    'Strike',
    'StrikeToUserAssociation',
    'UserRole',
    'StrikeToPlaceAssociation',
    'StrikeToItself',
)


class UserRole(enum.Enum):
    """
    Роль юзера в забастовке.
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
    М2М забастовка к юзеру (участие юзеров в забастовке).
    """
    __tablename__ = 'strike_to_user_associations'

    strike_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('strikes.id', ondelete='CASCADE', ),
        primary_key=True,
    )
    user_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE', ),
        primary_key=True,
    )
    role: Mapped[Enum | None] = mapped_column(
        Enum(UserRole, validate_strings=True),
    )
    user: Mapped['User'] = relationship(
        back_populates='strikes_where_involved',
    )
    strike: Mapped['Strike'] = relationship(
        back_populates='users_involved',
    )

    def __repr__(self):
        return f'Strike intermediate table: strike {self.strike_id}, user {self.user_id}'


class StrikeToPlaceAssociation(CreatedAtMixin, Base):
    """
    М2М Места проведения к забастовке.
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


class StrikeToItself(CreatedAtMixin, Base):
    """
    М2М забастовки на себя (групповая забастовка)
    """
    __tablename__ = 'strike_to_itself_associations'

    strike_left_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('strikes.id', ondelete='CASCADE', ),
        primary_key=True,
    )
    strike_right_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('strikes.id', ondelete='CASCADE', ),
        primary_key=True,
    )
    __table_args__ = (
        CheckConstraint(
            strike_left_id != strike_right_id,
            name='left_ne_right',
        ),
    )

    def __repr__(self):
        return f'Strike m2m {self.strike_left_id} <-> {self.strike_right_id}'


class Strike(CreatedUpdatedMixin, Base):
    """
    Забастовка.
    """
    __tablename__ = 'strikes'

    id: Mapped[BigIntPk]
    duration: Mapped[Range[datetime.datetime] | None] = mapped_column(
        TSTZRANGE(),
    )
    planned_on_date: Mapped[datetime.date | None]
    goals: Mapped[str] = mapped_column(Text())
    results: Mapped[str | None] = mapped_column(Text())
    overall_num_of_employees_involved: Mapped[int]
    enterprise_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('enterprises.id'),
    )
    created_by_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('users.id'),
    )
    union_in_charge_id: Mapped[BigIntType | None] = mapped_column(
        ForeignKey('unions.id', ondelete='SET NULL'),
    )
    group: Mapped[list['Strike']] = relationship(
        'Strike',
        secondary=StrikeToItself.__table__,
        passive_deletes=True,
        primaryjoin='Strike.id==StrikeToItself.strike_left_id',
        secondaryjoin='Strike.id==StrikeToItself.strike_right_id',
    )

    union: Mapped['Union'] = relationship(
        back_populates='strikes',
    )
    created_by: Mapped['User'] = relationship(
        back_populates='strikes_created_by_user',
    )
    users_involved: Mapped[set[StrikeToUserAssociation]] = relationship(
        back_populates='strike',
        passive_deletes=True,
        cascade='save-update, merge, delete, delete-orphan',
    )
    enterprise: Mapped['Enterprise'] = relationship(back_populates='strikes')
    user_ids: AssociationProxy[list[int]] = association_proxy('users_involved', 'user_id', )
    # для создания связи м2м с указанием роли юзера в промежуточной таблице
    users_involved_create: AssociationProxy[set[int]] = association_proxy(
        'users_involved', 'user_id',
        creator=lambda data: StrikeToUserAssociation(user_id=data['user_id'], role=data['role'])
    )

    places: Mapped[list['Place']] = relationship(
        secondary='strike_to_place_associations',
        passive_deletes=True,
        back_populates='strikes',
    )
    places_association_recs: Mapped[set['StrikeToPlaceAssociation']] = relationship(
        'StrikeToPlaceAssociation',
        passive_deletes=True,
        overlaps='places',
        cascade='save-update, merge, delete, delete-orphan',
    )
    # https://gist.github.com/jdittrich/3001e520d3872b12e2cb8e7d4a2472da
    places_ids: AssociationProxy[set[int]] = association_proxy(
        'places_association_recs',
        'place_id',
        creator=lambda _id: StrikeToPlaceAssociation(place_id=_id),
    )
    group_ids_ap: AssociationProxy[set[int]] = association_proxy(
        'group',
        'id',
    )
    group_ids_from_exp: Mapped[set[int]] = query_expression()

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
        UniqueConstraint(
            'planned_on_date', enterprise_id,
        )
    )

    def __repr__(self):
        return f'Strike {self.id} on enterprise {self.enterprise_id}'

    @validates('overall_num_of_employees_involved')
    def validate_overall_num_of_employees_involved(self, field, value):
        """
        Кол-во юзеров должно быть положительным интегром.
        """
        return positive_integer_only(field, value)

    @hybrid_property
    def is_active(self) -> ColumnElement[bool]:
        """
        Проходит ли забастовка на данный момент времени.
        """
        return self.duration.contains(datetime.datetime.now(tz=datetime.UTC))

    # noinspection PyNestedDecorators
    @is_active.inplace.expression
    @classmethod
    def _is_active_expression(cls) -> ColumnElement[bool]:
        """
        Проходит ли забастовка на данный момент времени.
        """
        return type_coerce(cls.duration.op('@>')(func.now()), Boolean)
