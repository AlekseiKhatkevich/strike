import jwt

from security.jwt import generate_jwt_token, validate_jwt_token, ALGORYTHM


def test_generate_and_validate_jwt_token():
    """
    Тест генерации и валидации jwt токена функциями generate_jwt_token и validate_jwt_token.
    """
    user_id = 100
    token = generate_jwt_token(user_id)
    user_id_from_token = validate_jwt_token(token)

    assert user_id_from_token == user_id

    headers = jwt.get_unverified_header(token)
    assert headers['alg'] == ALGORYTHM
    assert headers['kid'] == ''
    assert headers['typ'] == 'JWT'
