import datetime
from typing import TYPE_CHECKING, ClassVar, TypeVar

from email_validator import validate_email
from sqlalchemy import (
    String,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import (
    validates,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from internal.constants import EMAIL_REGEXP, BCRYPT_REGEXP
from internal.database import Base
from .annotations import BigIntPk
from .mixins import UpdatedAtMixin

if TYPE_CHECKING:
    from .auth import UsedToken
    from . import StrikeToUserAssociation

__all__ = (
    'User',
)

_T_EMAIL = TypeVar('_T_EMAIL', str, None)


class User(UpdatedAtMixin, Base):
    """
    Основная модель пользователя.
    """
    __tablename__ = 'users'

    id: Mapped[BigIntPk]

    name: Mapped[str] = mapped_column(
        String(64),
    )
    email: Mapped[str | None] = mapped_column(
        String(320),
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256),
        deferred=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    registration_date: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    used_token: Mapped['UsedToken'] = relationship(
        back_populates='user'
    )
    strikes_where_involved: Mapped[list['StrikeToUserAssociation']] = relationship(
            back_populates='user',
            passive_deletes=True,
        )
    strikes_created_by_user: Mapped[list['Strike']] = relationship(
        back_populates='created_by',
    )
    crud_logs: Mapped[list['CRUDLog']] = relationship(
        back_populates='user',
    )

    __table_args__ = (
        Index(
            'name_unique_idx',
            name,
            unique=True,
            postgresql_where=(is_active == True),
        ),
        Index(
            'email_unique_idx',
            email,
            unique=True,
            postgresql_where=(is_active == True),
        ),
        CheckConstraint(
            func.regexp_like(
                email,
                EMAIL_REGEXP,
            ),
            name='email',
        ),
        CheckConstraint(
            func.regexp_like(
                hashed_password,
                BCRYPT_REGEXP,
            ),
            name='hashed_password',
        ),
    )
    _cached_at: ClassVar[datetime.datetime]
    __repr__ = __str__ = lambda self: f'User "{self.name}" with id={self.id}'

    @validates('email')
    def validate_email(self, _, value: _T_EMAIL) -> _T_EMAIL:
        if value is None:
            return None
        emailinfo = validate_email(value, check_deliverability=False)
        return emailinfo.normalized
