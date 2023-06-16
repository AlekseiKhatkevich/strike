from sqlalchemy import String, CheckConstraint, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from internal.constants import OGRN_REGEXP
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk
from models.mixins import UpdatedAtMixin


class Enterprise(UpdatedAtMixin, Base):
    """

    """
    __tablename__ = 'enterprises'

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(
        String(256),
    )
    region_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('users.id', ondelete='PROTECT',),
    )
    place: Mapped[str] = mapped_column(
        Text(),
    )
    address: Mapped[str] = mapped_column(
        String(512),
    )
    field_of_activity: Mapped[str | None] = mapped_column(
        String(256),
    )
