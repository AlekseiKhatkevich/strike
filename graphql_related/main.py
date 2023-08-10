import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from graphql_related.mutations import Mutation
from graphql_related.queries import Query
from graphql_related.subscriptions import Subscription

__all__ = (
    'graphql_app',
    'schema',
)

from internal.dependencies import get_session


async def get_context(
        session=Depends(get_session),
):
    """
    Использование зависимостей FastApi
    https://strawberry.rocks/docs/integrations/fastapi#context_getter
    """
    return {
        'session': session,
    }


schema = strawberry.Schema(Query, Mutation, subscription=Subscription,)
graphql_app = GraphQLRouter(schema, context_getter=get_context,)
