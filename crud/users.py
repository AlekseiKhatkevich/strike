import datetime
from types import SimpleNamespace
from typing import TYPE_CHECKING

from sqlalchemy import Integer, func, select, true
from sqlalchemy.dialects.postgresql import ARRAY, Range
from sqlalchemy.orm import aliased

from crud.auth import check_invitation_token_used_already
from crud.helpers import commit_if_not_in_transaction
from models import CRUDLog, Strike, StrikeToUserAssociation, UsedToken, User
from models.exceptions import ModelEntryDoesNotExistsInDbError
from security.hashers import make_hash
from security.invitation import verify_invitation_token

if TYPE_CHECKING:
    from serializers.users import UserRegistrationSerializer
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'create_new_user',
    'get_user_by_id',
    'delete_user',
    'update_user',
    'active_users_view',
    'user_statistics',
)


@commit_if_not_in_transaction
async def get_user_by_id(session: 'AsyncSession',
                         user_id: int,
                         *,
                         raise_exc: bool = False,
                         only_active: bool = False,
                         ) -> User | None:
    """
    Получение юзера по id.
    """
    stmt = select(User).where(User.id == user_id)
    if only_active:
        stmt = stmt.where(User.is_active == True)
    user = await session.scalar(stmt)
    if user is None and raise_exc:
        raise ModelEntryDoesNotExistsInDbError(
            f'User with user_id {user_id} does not exists.',
            report=True,
        )
    return user


async def delete_user(session: 'AsyncSession', user: 'User') -> 'User':
    """
    Удаление юзера.
    """
    await session.delete(user)
    await session.commit()
    return user


async def update_user(session: 'AsyncSession',
                      user: 'User',
                      user_data: dict,
                      ) -> 'User':
    """
    Обновляем данный юзера.
    """
    if (new_password := user_data.get('password')) is not None:
        user.hashed_password = make_hash(new_password.get_secret_value())
    for field, value in user_data.items():
        setattr(user, field, value)
    await session.commit()
    return user


async def create_new_user(session: 'AsyncSession', user_data: 'UserRegistrationSerializer') -> User:
    """
    Создание нового пользователя в БД.
    """
    await check_invitation_token_used_already(session, user_data.invitation_token.get_secret_value())
    decoded_token = verify_invitation_token(
        token=user_data.invitation_token,
        username=user_data.name,
        password=user_data.invitation_password,
    )
    hashed_password = make_hash(user_data.password.get_secret_value())

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    used_token = UsedToken(
        token=user_data.invitation_token.get_secret_value(),
        issued_at=datetime.datetime.fromtimestamp(decoded_token['iat']).astimezone(datetime.UTC),
    )

    user.used_token = used_token
    session.add(user)
    await session.commit()
    return user


active_users_view = aliased(
    User, select(User).where(User.is_active == True).subquery(), name='active_users',
)


async def user_statistics(session: 'AsyncSession',
                          user_id: int,
                          period: Range[datetime.datetime],
                          ) -> SimpleNamespace:
    """
    Статистка юзера.
    """
    user_stats = SimpleNamespace(user_id=user_id)

    rank_by_action_sq = select(
        CRUDLog.user_id,
        CRUDLog.action,
        func.count('*').label('cnt'),
        func.rank().over(partition_by=CRUDLog.action, order_by=func.count('*').desc()).label('rnk'),
    ).where(
        CRUDLog.user_id.is_not(None),
        CRUDLog.operation_ts.op('<@')(period)
    ).group_by(
        CRUDLog.user_id,
        CRUDLog.action,
    ).subquery()

    # noinspection PyTypeChecker
    action_cnt_rnk = select(
        rank_by_action_sq.c.action,
        rank_by_action_sq.c.cnt,
        rank_by_action_sq.c.rnk,
    ).where(
        rank_by_action_sq.c.user_id == user_id,
    )

    for action, count, rank in (await session.execute(action_cnt_rnk)).all():
        setattr(user_stats, action.name, dict(count=count, rank=rank))

    strike_ids = select(
        func.array_agg(
            StrikeToUserAssociation.strike_id, type_=ARRAY(Integer)
        ).label('strikes_involved_ids'),
    ).where(
        StrikeToUserAssociation.user_id == Strike.created_by_id,
    ).lateral()

    strikes_stats = select(
        func.nullif(func.count('*'), 0).label('num_strikes_created'),
        strike_ids.c.strikes_involved_ids,
    ).select_from(
        Strike
    ).where(
        Strike.created_by_id == user_id,
        Strike.created_at.op('<@')(period),
    ).group_by(
        strike_ids.c.strikes_involved_ids,
    ).join_from(
        Strike, strike_ids, true()
    )

    strike_stats = (await session.execute(strikes_stats)).one_or_none()
    if strike_stats is not None:
        user_stats.__dict__.update(strike_stats._mapping)

    return user_stats
