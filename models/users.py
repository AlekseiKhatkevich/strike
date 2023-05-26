import datetime

from email_validator import validate_email
from sqlalchemy import (
    Boolean,
    Column,
    String,
    BigInteger,
    TIMESTAMP,
    Index,
    CheckConstraint,
    Identity,
)
from sqlalchemy.orm import validates, Mapped, mapped_column
from sqlalchemy.sql import func


from constants import EMAIL_REGEXP
from database import Base

__all__ = (
    'User',
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(320),
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    registration_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
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
    )

    def __str__(self) -> str:
        return f'User {self.name} with id={self.id}'

    @validates("email")
    def validate_email(self, _, value: str) -> str:
        emailinfo = validate_email(value, check_deliverability=False)
        return emailinfo.normalized
