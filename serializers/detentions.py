import datetime
import enum
from typing import Literal

from pydantic import ConfigDict, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from sqlalchemy.dialects.postgresql import Range

from internal.serializers import BaseModel, PastAwareDatetime
from models.initial_data import RU_regions
from serializers.helpers import RangeField
from serializers.typing import IntIdType

__all__ = (
    'WSDetentionOutSerializer',
    'WSActionType',
    'WSDataCreateUpdateSerializer',
    'WSDataGetDeleteSerializer',
    'WSForLawyerInSerializer',
    'WsForLawyerOutSerializer',
    'JailOutSerializer',
    'DetentionDailyStatsOutSerializer',
)

duration_input_type = Range[datetime.datetime] | list[datetime.datetime, datetime.datetime | None]


class WSActionType(str, enum.Enum):
    """
    Типы действий в ЭП WS.
    """
    get_detentions = 'GET_DETENTIONS'
    create_detention = 'CREATE_DETENTIONS'
    update_detention = 'UPDATE_DETENTIONS'
    delete_detentions = 'DELETE_DETENTIONS'


class WSDataBaseSerializer(BaseModel):
    """
    Базовый сериалайзер для операций через WS.
    """
    duration: RangeField
    name: str
    extra_personal_info: str | None
    needs_medical_attention: bool = False
    needs_lawyer: bool = False
    jail_id: IntIdType
    charge: str | None = None
    transferred_from_id: IntIdType | None = None
    relative_or_friend: str | None = None

    _for_type: WSActionType


class WSDataCreateUpdateSerializer(WSDataBaseSerializer):
    """
    Для создания или обновления заключения.
    """
    id: IntIdType | None = None


class WSDataGetDeleteSerializer(BaseModel):
    """
    Для передачи id (GET & DELETE).
    """
    id: IntIdType


class WSDetentionOutSerializer(BaseModel):
    """
    Отдача инфы на фронт о заключении человека.
    """
    duration: RangeField
    name: str
    extra_personal_info: str | None
    needs_medical_attention: bool
    needs_lawyer: bool
    jail_id: IntIdType
    charge: str | None
    transferred_from_id: IntIdType | None
    relative_or_friend: str | None

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @field_validator('duration', mode='before')
    @classmethod
    def _unpack_duration_if_needed(cls, duration: duration_input_type,
                                   info: FieldValidationInfo,
                                   ) -> list[datetime.datetime, datetime.datetime | None]:
        if isinstance(duration, Range):
            return [duration.lower, duration.upper]
        else:
            return duration


class WSForLawyerInSerializer(BaseModel):
    """
    Для получения настроек ЭП '/ws/lawyer' с фронта.
    """
    regions: list[Literal[*RU_regions.names]] | None = None
    start_date: PastAwareDatetime = datetime.datetime.min.replace(tzinfo=datetime.UTC)
    jail_ids: list[IntIdType] | None = None


class JailOutSerializer(BaseModel):
    """
    Для отдачи инфы о крытой на фронт.
    """
    id: IntIdType
    address: str
    region_id: str

    model_config = ConfigDict(from_attributes=True,)


class WsForLawyerOutSerializer(WSDetentionOutSerializer):
    """
    Для отдачи инф на фронт через вебсокет '/ws/lawyer'.
    """
    jail: JailOutSerializer

    model_config = ConfigDict(extra='forbid', )


class DetentionDailyStatsOutSerializer(BaseModel):
    """
    Для отдачи ежедневной статистики на фронт.
    """
    jail_id: int
    zk_count: int
    date: datetime.date

    model_config = ConfigDict(from_attributes=True,)
