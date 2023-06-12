import events.user_evetns

__all__ = (
    'register_all_sqlalchemy_events',
)


def register_all_sqlalchemy_events() -> None:
    """
    Регистрирует все эвенты sqlachemy с нашими хендлерами. Используется в lifespan.
    """
    events.user_evetns.register()
