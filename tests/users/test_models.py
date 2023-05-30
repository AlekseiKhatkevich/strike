import datetime




async def test_user_model_creation_positive(db_session, user_factory):
    """

    """
    async with db_session.begin():
        user = user_factory.build()
        db_session.add(user)

    async with db_session.begin():
        await db_session.refresh(user)
        assert user.id is not None

        await user.awaitable_attrs.hashed_password
        await user.awaitable_attrs.updated_at

        assert user.is_active
        assert user.updated_at is None
        assert user.registration_date.tzinfo == datetime.UTC



def test_ping(client):
    response = client.get('/users/ping/')
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
