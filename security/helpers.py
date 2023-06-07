__all__ = (
    'sensitive',
)


def sensitive(text: str) -> str:
    """
    Заменяет центр пароля звездочками
    """
    keep = len(text) // 5
    return text[:keep] + '*****' + text[-keep:]
