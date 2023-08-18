import datetime
import operator

import grpc
import pytest
from sqlalchemy.dialects.postgresql import Range

from internal.database import async_session
from serializers.proto.compiled import conflicts_pb2


pytestmark = pytest.mark.usefixtures('truncate_db_func_scope')


# https://github.com/alexykot/grpcio-test-example/blob/master/example/test_greeter_server.py


async def test_ListConflicts_positive(two_conflicts, get_grpc_response):
    """
    Позитивный метод сервиса ListConflicts.
    """
    request = conflicts_pb2.MultipleConflictsRequest()

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK

    for conflict_response, conflict_entry in zip(response.conflicts, two_conflicts):
        assert conflict_response.conflict.id == conflict_entry.id
        pb_enum_name = conflicts_pb2.ConflictTypes.Name(conflict_response.conflict.type)
        assert pb_enum_name == conflict_entry.type.name
        lower = conflict_response.conflict.duration.lower.ToDatetime(tzinfo=datetime.UTC)
        upper = conflict_response.conflict.duration.upper.ToDatetime(tzinfo=datetime.UTC)
        assert lower == conflict_entry.duration.lower
        assert upper == conflict_entry.duration.upper
        assert conflict_response.conflict.enterprise_id == conflict_entry.enterprise_id
        assert conflict_response.conflict.description == conflict_entry.description
        assert (round(conflict_response.conflict.success_rate, 2) ==
                round(conflict_entry.success_rate, 2))
        assert (conflict_response.extra_data.created_at.ToDatetime(tzinfo=datetime.UTC) ==
                conflict_entry.created_at)


async def test_ListConflicts_filter_by_id(two_conflicts, get_grpc_response):
    """
    Фильтрация по первичному ключу Конфликта.
    """
    conflict_id = two_conflicts[0].id
    request = conflicts_pb2.MultipleConflictsRequest(id=[conflict_id])

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK
    assert len(response.conflicts) == 1
    assert response.conflicts[0].conflict.id == conflict_id


async def test_ListConflicts_filter_by_conflict_type(two_conflicts, get_grpc_response):
    """
    Фильтрация по первичному типу Конфликта.
    """
    _type = two_conflicts[0].type.name
    _id = two_conflicts[0].id
    request = conflicts_pb2.MultipleConflictsRequest(type=[_type])

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK
    assert len(response.conflicts) == 1
    pb_enum_name = conflicts_pb2.ConflictTypes.Name(response.conflicts[0].conflict.type)
    assert pb_enum_name == _type
    assert response.conflicts[0].conflict.id == _id


async def test_ListConflicts_filter_by_duration(conflict_factory, get_grpc_response):
    """
    Фильтрация по длительности Конфликта.
    """
    duration1 = Range(
        datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC),
        datetime.datetime(1971, 1, 1, tzinfo=datetime.UTC),
    )
    duration2 = Range(
        datetime.datetime(1980, 1, 1, tzinfo=datetime.UTC),
        datetime.datetime(1981, 1, 1, tzinfo=datetime.UTC),
    )
    conflict1 = conflict_factory.build(duration=duration1)
    conflict2 = conflict_factory.build(duration=duration2)

    async with async_session() as session:
        session.add_all([conflict1, conflict2])
        await session.commit()

    request = conflicts_pb2.MultipleConflictsRequest()
    request.duration.lower.FromDatetime(datetime.datetime(1969, 1, 1, tzinfo=datetime.UTC))
    request.duration.upper.FromDatetime(datetime.datetime(1971, 1, 1, tzinfo=datetime.UTC))

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK
    assert len(response.conflicts) == 1
    assert response.conflicts[0].conflict.id == conflict1.id


async def test_ListConflicts_filter_by_enterprise_id(two_conflicts, get_grpc_response):
    """
    Фильтрация по компании Конфликта.
    """
    enterprise_id = two_conflicts[0].enterprise_id
    _id = two_conflicts[0].id
    request = conflicts_pb2.MultipleConflictsRequest(enterprise_id=[enterprise_id])

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK
    assert len(response.conflicts) == 1
    assert response.conflicts[0].conflict.enterprise_id == enterprise_id
    assert response.conflicts[0].conflict.id == _id


@pytest.mark.parametrize('comp', ['gte', 'lte'])
async def test_ListConflicts_filter_by_success_rate(comp, two_conflicts, get_grpc_response):
    """
    Фильтрация по критерию успешности Конфликта.
    """
    op = operator.le if comp == 'lte' else operator.ge
    request = conflicts_pb2.MultipleConflictsRequest()
    setattr(request.success_rate, comp, 0.5)
    conflicts_ids = {
        conflict.id for conflict in two_conflicts if op(conflict.success_rate, 0.5)
    }

    response, _, code, _ = await get_grpc_response('ListConflicts', request)

    assert code == grpc.StatusCode.OK

    response_ids = {conflict.conflict.id for conflict in response.conflicts}

    assert response_ids == conflicts_ids
