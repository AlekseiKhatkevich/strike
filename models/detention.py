import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint, Range
from sqlalchemy.orm import (
    Mapped,
    column_property,
    deferred,
    mapped_column,
    relationship,
)

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

__all__ = (
    'Detention',
    'Jail',
)


class Detention(Base):
    """
    Задержание мусарами.
    """
    __tablename__ = 'detentions'

    id: Mapped[BigIntPk]
    duration: Mapped[Range[datetime.datetime]]
    name: Mapped[str] = mapped_column(
        String(collation=RU_RU_CE_COLLATION_NAME),
        index=True,
    )
    extra_personal_info: Mapped[str | None]
    needs_medical_attention: Mapped[bool] = False
    needs_lawyer: Mapped[bool] = False
    jail_id: Mapped[BigIntType] = mapped_column(
        ForeignKey('jails.id', ondelete='RESTRICT')
    )
    charge: Mapped[str | None]
    transferred_from_id: Mapped[BigIntType | None] = mapped_column(
        ForeignKey('detentions.id', ondelete='RESTRICT')
    )
    relative_or_friend: Mapped[str | None]

    jail: Mapped['Jail'] = relationship(back_populates='zk')

    def __repr__(self):
        return f'{self.name} находиться в крытой {self.jail_id}.'

    __table_args__ = (
        ExcludeConstraint(
            (Column('duration'), '&&'),
            (Column('name'), '='),
            name='duration_name_exc_constraint',
        ),
        CheckConstraint(
            ~ func.lower_inf('duration'),
            name='duration_has_start_dt',
        )
    )


class Jail(Base):
    """
    Крытая.
    """
    __tablename__ = 'jails'

    id: Mapped[BigIntPk] = mapped_column()
    name: Mapped[str] = mapped_column(
        String(collation=RU_RU_CE_COLLATION_NAME),
    )
    address: Mapped[str]
    region_id: Mapped[str] = mapped_column(
        ForeignKey('regions.name', ondelete='RESTRICT'),
    )

    zk_count = deferred(column_property(
        select(func.count('*')).where(
            Detention.jail_id == id,
            Detention.duration.op('@>')(func.now()),
        ).correlate_except(Detention).scalar_subquery()
    )
    )

    region: Mapped['Region'] = relationship()
    zk: Mapped['Detention'] = relationship(back_populates='jail')

    def __repr__(self):
        return f'Крытая "{self.name}" в регионе {self.region_id}.'

    __table_args__ = (
        UniqueConstraint(name, region_id),
    )

    @property
    def has_zk(self) -> bool:
        return self.zk_count > 0
