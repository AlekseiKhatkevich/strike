import datetime
import enum

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_relationship

from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

__all__ = (
    'CRUDLog',
    'CRUDTypes',
)


class CRUDTypes(enum.Enum):
    """
    Типы действий с объектами.
    """
    create = 'CREATE'
    update = 'UPDATE'
    delete = 'DELETE'
    add = 'ADD'
    remove = 'REMOVE'


class CRUDLog(Base):
    """
    Лог действий с объектами.
    """
    __tablename__ = 'crud_logs'

    id: Mapped[BigIntPk]
    object_type: Mapped[str] = mapped_column(
        String(255),
    )
    object_id: Mapped[BigIntType]
    action: Mapped[ENUM] = mapped_column(
        ENUM(CRUDTypes, validate_strings=True),
    )
    operation_ts: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    user_id: Mapped[BigIntType | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
    )

    object = generic_relationship(object_type, 'object_id')
    user: Mapped['User'] = relationship(
        back_populates='crud_logs',
    )

    __table_args__ = (
        Index(
            'type_object_id_idx',
            'object_type', 'object_id',
            postgresql_include=['action'],
        ),
        Index(
            'operation_ts_brin_idx',
            'operation_ts',
            postgresql_using='brin',
        )
    )

    def __repr__(self):
        return f'{self.action} {self.object_type} with id = {self.object_id}'
