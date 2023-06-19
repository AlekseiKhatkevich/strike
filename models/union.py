from sqlalchemy.orm import Mapped, mapped_column

from internal.database import Base
from models.annotations import BigIntPk
from models.mixins import UpdatedAtMixin, CreatedAtMixin

__all__ = (
    'Union',
)


class Union(UpdatedAtMixin, CreatedAtMixin, Base):
    """
    """
    __tablename__ = 'unions'

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(
        unique=True,
    )
    is_yellow: Mapped[bool] = mapped_column(
        default=False,
    )


