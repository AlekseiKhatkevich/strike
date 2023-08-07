from typing import TYPE_CHECKING

from internal.typing_and_types import MODEL_T

if TYPE_CHECKING:
    from google._upb._message import MessageMeta

__all__ = (
    'pb_from_model_instance',
)


def pb_from_model_instance(pb: 'MessageMeta', instance: MODEL_T) -> 'MessageMeta':
    """
    Запихивает аттрибуты интанса модели в буффер предварительно его инициализировав.
    """
    buff = pb()
    for filed_name in buff.DESCRIPTOR.fields_by_name.keys():
        setattr(buff, filed_name, getattr(instance, filed_name))

    if not buff.IsInitialized():
        raise AttributeError(f' Not all attributes are set for buffer {type(buff)}')

    return buff
