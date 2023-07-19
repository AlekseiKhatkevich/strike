import datetime
import enum

from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_relationship

from internal.database import Base
from models.annotations import BigIntPk

__all__ = (
    'CRUDLog',
)


class CRUDTypes(enum.Enum):
    """
    """
    create = 'CREATE'
    update = 'UPDATE'
    delete = 'DELETE'


class CRUDLog(Base):
    """

    """
    __tablename__ = 'crud_logs'

    id: Mapped[BigIntPk]
    object_type = String(255)
    object_id: Mapped[BigIntPk]
    action: Mapped[ENUM] = mapped_column(
        ENUM(CRUDTypes, validate_strings=True),
    )
    operation_ts: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    object = generic_relationship(object_type, 'object_id')