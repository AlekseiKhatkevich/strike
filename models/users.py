from email_validator import validate_email
from sqlalchemy import (
    Boolean,
    Column,
    String,
    BigInteger,
    TIMESTAMP,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import validates
from sqlalchemy.sql import func


from constants import EMAIL_REGEXP
from database import Base

__all__ = (
    'User',
)


class User(Base):
    __tablename__ = 'users'

    id = Column(
        BigInteger,
        primary_key=True,
        # index=True,
    )
    name = Column(
        String(64),
        nullable=False,
    )
    email = Column(
        String(320),
    )
    hashed_password = Column(
        String(256),
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    registration_date = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        # nullable=False,
        server_onupdate=func.now(),
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
