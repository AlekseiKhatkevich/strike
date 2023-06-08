
__all__ = (
    'GeneralModelError',
    'ModelEntryDoesNotExistsInDbError',
)


class GeneralModelError(Exception):
    """
    Общий класс исключений связанный с моделями.
    """
    _default_text = 'Shit happens.'

    def __init__(self, text=_default_text):
        self.text = text


class ModelEntryDoesNotExistsInDbError(GeneralModelError):
    """
    Записи в БД не найдено.
    """
    _default_text = 'Model entry does not exists.'
    pass
