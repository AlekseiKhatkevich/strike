import strawberry
from strawberry.fastapi import GraphQLRouter

from graphql_related.mutations import Mutation
from graphql_related.queries import Query
from graphql_related.subscriptions import Subscription

__all__ = (
    'graphql_app',
)

schema = strawberry.Schema(Query, Mutation, subscription=Subscription)
graphql_app = GraphQLRouter(schema)
