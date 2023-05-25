from sqlalchemy import Boolean, Column, String, BigInteger, DateTime, TIMESTAMP
from sqlalchemy.sql import func

from database import Base

__all__ = (
    'User',
)


class User(Base):
    __tablename__ = 'users'

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )
    name = Column(
        String(64),
        nullable=False,
    )
    email = Column(
        String(320),
        unique=True,
        index=True,
    )  #todo check constraint
    hashed_password = Column(
        String(256),
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
    )
    registration_date = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )# todo в какой таймзоне сохраняет
    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
    )

    def __str__(self):
        return f'User with {self.id=}'
