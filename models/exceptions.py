
__all__ = (
    'GeneralModelError',
    'ModelEntryDoesNotExistsInDbError',
)


class GeneralModelError(Exception):
    """
    Общий класс исключений связанный с моделями.
    self.report должен быть True для обработки исключения обработчиком
    model_does_not_exists_exception_handler
    """
    _default_text = 'Shit happens.'
    reportable = False

    def __init__(self, text: str = _default_text, report: bool = False):
        self.text = text
        self.report = self.reportable and report

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, reportable, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.reportable = reportable


class ModelEntryDoesNotExistsInDbError(GeneralModelError, reportable=True):
    """
    Записи в БД не найдено.
    """
    _default_text = 'Model entry does not exists.'
    pass
