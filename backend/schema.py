"""Ax GraphQL schema
Combines all Ax GraphQL schemas to one
"""

import graphene
from graphene import relay
from backend.schemas.users_schema import UsersQuery, UsersMutations, UsersSubscription, Users
from backend.schemas.home_schema import HomeQuery


class Query(UsersQuery, HomeQuery, graphene.ObjectType):
    """Combines all schemas queryes"""
    node = relay.Node.Field()
    hello = graphene.String(argument=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, argument):
        """Test function"""
        del info  # not used
        return 'Hello ' + argument


class Mutations(UsersMutations, graphene.ObjectType):
    """Combines all schemas mutations"""


class Subscription(UsersSubscription, graphene.ObjectType):
    """Combines all schemas subscription"""


schema = graphene.Schema(
    query=Query,
    mutation=Mutations,
    types=[Users],
    subscription=Subscription
)
