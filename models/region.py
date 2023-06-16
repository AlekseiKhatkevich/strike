from sqlalchemy.orm import Mapped, mapped_column

from internal.database import Base

__all__ = (
    'Region',
)


class Region(Base):
    """
    """
    __tablename__ = 'regions'

    name: Mapped[str] = mapped_column(
        primary_key=True,
    )
