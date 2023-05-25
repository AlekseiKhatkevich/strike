from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

# __all__ = (
#     'Base',
#     'engine',
# )

engine = create_async_engine(
    settings.pg_dsn,
    echo=True,
    echo_pool=True,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


from sqlalchemy import Boolean, Column, Integer, String




# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)