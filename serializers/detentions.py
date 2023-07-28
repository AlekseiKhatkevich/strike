import enum

from pydantic import ConfigDict, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from sqlalchemy.dialects.postgresql import Range

from internal.serializers import BaseModel
from serializers.helpers import RangeField
from serializers.typing import IntIdType

__all__ = (
    'WSDetentionOutSerializer',
    'WSActionType',
    'WSDataCreateUpdateSerializer',
    'WSDataGetDeleteSerializer',
)


class WSActionType(str, enum.Enum):
    """

    """
    get_detentions = 'GET_DETENTIONS'
    create_detention = 'CREATE_DETENTIONS'
    update_detention = 'UPDATE_DETENTIONS'
    delete_detentions = 'DELETE_DETENTIONS'


class WSDataBaseSerializer(BaseModel):
    """

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

    """
    id: IntIdType | None = None
    # _for_type = WSActionType.create_detention


# class WSDataUpdateSerializer(WSDataBaseSerializer):
#     id: IntIdType
#     _for_type = WSActionType.update_detention
#

class WSDataGetDeleteSerializer(BaseModel):
    id: IntIdType


# class WSDataGetSerializer(WSDataBaseSerializer):
#     ids: list[IntIdType]
#     _for_type = WSActionType.get_detentions


# class DetentionsWSSerializer(BaseModel):
#     """
#
#     """
#     action: WSActionType
#     data: (WSDataCreateSerializer |
#            WSDataUpdateSerializer |
#            WSDataDeleteSerializer |
#            WSDataGetSerializer)
#
#     # noinspection PyNestedDecorators
#     @field_validator('data')
#     @classmethod
#     def validate_for_type(cls, data: WSDataBaseSerializer,
#                           info: FieldValidationInfo,
#                           ) -> WSDataBaseSerializer:
#         """
#
#         """
#         if (nested_action := data._for_type) != (action := info.data['action']):
#             raise ValueError(
#                 f'Action and data mismatch!. You specified action "{action}" but "data" provided'
#                 f' is for "{nested_action}".'
#             )
#         else:
#             return data
#

class WSDetentionOutSerializer(BaseModel):
    """

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

    @field_validator('duration', mode='before')
    @classmethod
    def validate_for_type(cls, duration, info: FieldValidationInfo):
        if isinstance(duration, Range):
            return [duration.lower, duration.upper]
        else:
            return duration

