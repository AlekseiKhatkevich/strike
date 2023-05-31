import pytest

from serializers.users import password_strength_error_message


# noinspection PyPep8Naming
def test_UserRegistrationSerializer_positive(user_registration_serializer_factory):
    """
    Позитивный тест сериалайзера UserRegistrationSerializer сериализации
    ПОСТ данных эндпойнта регистрации юзера.
    """
    user_registration_serializer_factory.build()


# noinspection PyPep8Naming
def test_UserRegistrationSerializer_negative(user_registration_serializer_factory):
    """
    Негативный тест сериалайзера UserRegistrationSerializer. Слабый пароль.
    """
    with pytest.raises(ValueError, match=password_strength_error_message):
        user_registration_serializer_factory.build(password='test')