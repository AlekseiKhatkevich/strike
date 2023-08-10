import datetime

from graphql_related.main import schema


async def test_new_strikes(strike_factory, db_session):
    """
    Позитивный тест подписки new_strikes.
    """
    strikes = strike_factory.build_batch(size=3)
    db_session.add_all(strikes)
    await db_session.commit()

    query = """
    subscription NewStrikes {
    newStrikes(gtDt: "%s") {
        id
        duration
        plannedOnDate
        goals
        results
        overallNumOfEmployeesInvolved
        enterpriseId
        createdById
        unionInChargeId
    }
}
    """ % datetime.datetime.min.replace(tzinfo=datetime.UTC).isoformat()

    sub = await schema.subscribe(query, context_value={'session': db_session})

    index = 0
    strike_ids = set()

    async for result in sub:
        assert not result.errors
        strike_ids.add(result.data['newStrikes']['id'])

        index += 1
        if index == len(strikes):
            break

    assert strike_ids == {s.id for s in strikes}
