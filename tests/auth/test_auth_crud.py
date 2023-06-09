from crud.auth import authenticate_user


async def test_authenticate_user_positive(db_session, user_in_db):
    """
    Позитивный тест ф-ции аутентификации изера по логину и паролю authenticate_user.
    """
    authenticated_user = await authenticate_user(db_session, user_in_db.name, '1q2w3e')
    assert authenticated_user is user_in_db


async def test_authenticate_user_no_user(db_session, caplog):
    """
    Негативные тест ф-ции аутентификации изера по логину и паролю authenticate_user.
    Юзера не существует.
    """
    name = 'fake_name'
    authenticated_user = await authenticate_user(db_session, name, '1q2w3e')
    assert not authenticated_user
    assert f'User with name {name} does not exists or inactive.' in caplog.text


async def test_authenticate_user_wrong_password(db_session, caplog, user_in_db):
    """
    Негативные тест ф-ции аутентификации изера по логину и паролю authenticate_user.
    Юзера существует, но пароль не верен.
    """
    authenticated_user = await authenticate_user(db_session, user_in_db.name, 'wrong_password')
    assert not authenticated_user
    assert f'User with name {user_in_db.name} provided incorrect password' in caplog.text
