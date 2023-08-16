from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConflictTypes(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[ConflictTypes]
    PAYMENT: _ClassVar[ConflictTypes]
    LAYOFF: _ClassVar[ConflictTypes]
    LIQUIDATION: _ClassVar[ConflictTypes]
    OTHER: _ClassVar[ConflictTypes]
    DISMISSAL: _ClassVar[ConflictTypes]
    MANAGEMENT_POLITICS: _ClassVar[ConflictTypes]
    WORK_CONDITIONS: _ClassVar[ConflictTypes]
    LABOR_HOURS: _ClassVar[ConflictTypes]
    COLLECTIVE_AGREEMENT: _ClassVar[ConflictTypes]
    PAYMENT_DELAY: _ClassVar[ConflictTypes]
    LABOUR_RIGHTS: _ClassVar[ConflictTypes]
UNSPECIFIED: ConflictTypes
PAYMENT: ConflictTypes
LAYOFF: ConflictTypes
LIQUIDATION: ConflictTypes
OTHER: ConflictTypes
DISMISSAL: ConflictTypes
MANAGEMENT_POLITICS: ConflictTypes
WORK_CONDITIONS: ConflictTypes
LABOR_HOURS: ConflictTypes
COLLECTIVE_AGREEMENT: ConflictTypes
PAYMENT_DELAY: ConflictTypes
LABOUR_RIGHTS: ConflictTypes

class Conflict(_message.Message):
    __slots__ = ["id", "type", "duration", "enterprise_id", "description", "results", "success_rate"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    ENTERPRISE_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: ConflictTypes
    duration: Duration
    enterprise_id: int
    description: str
    results: str
    success_rate: float
    def __init__(self, id: _Optional[int] = ..., type: _Optional[_Union[ConflictTypes, str]] = ..., duration: _Optional[_Union[Duration, _Mapping]] = ..., enterprise_id: _Optional[int] = ..., description: _Optional[str] = ..., results: _Optional[str] = ..., success_rate: _Optional[float] = ...) -> None: ...

class SingleConflictResponse(_message.Message):
    __slots__ = ["conflict", "extra_data"]
    CONFLICT_FIELD_NUMBER: _ClassVar[int]
    EXTRA_DATA_FIELD_NUMBER: _ClassVar[int]
    conflict: Conflict
    extra_data: ConflictExtraData
    def __init__(self, conflict: _Optional[_Union[Conflict, _Mapping]] = ..., extra_data: _Optional[_Union[ConflictExtraData, _Mapping]] = ...) -> None: ...

class ConflictExtraData(_message.Message):
    __slots__ = ["updated_at", "created_at"]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    updated_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Duration(_message.Message):
    __slots__ = ["lower", "upper"]
    LOWER_FIELD_NUMBER: _ClassVar[int]
    UPPER_FIELD_NUMBER: _ClassVar[int]
    lower: _timestamp_pb2.Timestamp
    upper: _timestamp_pb2.Timestamp
    def __init__(self, lower: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., upper: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EmptyResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class SingleIdRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class MultipleConflictsRequest(_message.Message):
    __slots__ = ["id", "type", "duration", "enterprise_id", "success_rate"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    ENTERPRISE_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    id: _containers.RepeatedScalarFieldContainer[int]
    type: _containers.RepeatedScalarFieldContainer[ConflictTypes]
    duration: Duration
    enterprise_id: _containers.RepeatedScalarFieldContainer[int]
    success_rate: SuccessRate
    def __init__(self, id: _Optional[_Iterable[int]] = ..., type: _Optional[_Iterable[_Union[ConflictTypes, str]]] = ..., duration: _Optional[_Union[Duration, _Mapping]] = ..., enterprise_id: _Optional[_Iterable[int]] = ..., success_rate: _Optional[_Union[SuccessRate, _Mapping]] = ...) -> None: ...

class SuccessRate(_message.Message):
    __slots__ = ["success_rate_gte", "success_rate_lte"]
    SUCCESS_RATE_GTE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_LTE_FIELD_NUMBER: _ClassVar[int]
    success_rate_gte: float
    success_rate_lte: float
    def __init__(self, success_rate_gte: _Optional[float] = ..., success_rate_lte: _Optional[float] = ...) -> None: ...

class MultipleConflictsResponse(_message.Message):
    __slots__ = ["conflict"]
    CONFLICT_FIELD_NUMBER: _ClassVar[int]
    conflict: _containers.RepeatedCompositeFieldContainer[SingleConflictResponse]
    def __init__(self, conflict: _Optional[_Iterable[_Union[SingleConflictResponse, _Mapping]]] = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ["code", "message", "details"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    details: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...
