import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DATE, ForeignKey,
    Index, String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint, INTERVAL, Range
from sqlalchemy.orm import (
    Mapped,
    column_property,
    deferred,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import create_materialized_view, refresh_materialized_view
from sqlalchemy_utils.view import CreateView, DropView

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

__all__ = (
    'Detention',
    'Jail',
    'DetentionMaterializedView',
)

from models.mixins import MaterializedViewMixin


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


class DetentionMaterializedView(MaterializedViewMixin, Base):
    """
    Материализованное представление статистики сидельцев по дням на каждую крытую.
    https://github.com/kvesteri/sqlalchemy-utils/issues/457#issuecomment-1432453337
    Пример:
     +-------+-------+----------+
    |jail_id|zk_count|date   |
    +-------+-------+----------+
    |1      |1      |2023-07-30|
    |1      |1      |2023-08-01|
    |1      |1      |2023-07-31|
    |1      |1      |2023-07-27|
    |1      |1      |2023-07-28|
    |1      |1      |2023-08-02|
    |5      |23     |2023-07-29|
    |5      |1      |2023-07-27|
    |1      |1      |2023-07-29|
    |5      |23     |2023-07-28|
    +-------+-------+----------+
    """
    jail_id: Mapped[BigIntPk]
    zk_count: Mapped[int]
    date: Mapped[datetime.date]

    __tablename__ = 'detentions_stats_per_day'
    _refresh_period: float = 3600

    _selectable = select(
            Detention.jail_id,
            func.count(Detention.id).label('zk_count'),
            func.cast(
                func.generate_series(
                    func.date_trunc('day', func.lower(Detention.duration)),
                    func.coalesce(func.date_trunc('day', func.upper(Detention.duration)), func.current_date()),
                    func.cast(func.concat(1, ' DAY'), INTERVAL)),
                DATE,
            ).label('date')
        ).group_by(
            Detention.jail_id,
            'date',
        )

    __table__ = create_materialized_view(
        __tablename__,
        _selectable,
        Base.metadata,
        indexes=[Index('date_jail_idx', 'date', 'jail_id', unique=True)]
    )

    def __repr__(self):
        return f'{self.date} was {self.zk_count} zk in jail with id {self.jail_id}'
