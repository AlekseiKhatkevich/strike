import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Index,
    Text,
    ForeignKey, func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from internal.database import Base
from internal.typing_and_types import BigIntType
from .annotations import BigIntPk

if TYPE_CHECKING:
    from .users import User


__all__ = (
    'UsedToken',
    'CommonPassword',
)


class UsedToken(Base):
    """
    Список использованных пригласительных токенов.
    """
    __tablename__ = 'used_tokens'

    id: Mapped[BigIntPk]
    user_id: Mapped[BigIntType | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL',),
    )
    token: Mapped[str]
    issued_at: Mapped[datetime.datetime]

    used_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    user: Mapped['User'] = relationship(
        back_populates='used_token',
    )

    __table_args__ = (
        Index(
            'token_hash_idx',
            'token',
            postgresql_using='hash',
        ),
    )

    __repr__ = __str__ = lambda self: f'Token used by user {self.user_id = }'


class CommonPassword(Base):
    """
    Список самых распространенных паролей.
    """
    __tablename__ = 'common_passwords'

    id: Mapped[BigIntPk]

    password: Mapped[str] = mapped_column(
        Text(collation='english_ci'),
    )

    __table_args__ = (
        Index(
            'password_hash_idx',
            password,
            postgresql_using='hash',
            postgresql_with={'fillfactor': 100},
        ),
    )

    __repr__ = __str__ = lambda self: self.password
