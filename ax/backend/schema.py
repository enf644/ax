"""Ax GraphQL schema
Combines all Ax GraphQL schemas to one
"""
import sys
import graphene
from graphene import relay
from loguru import logger
from backend.schemas.users_schema import User, UsersQuery
from backend.schemas.users_schema import UsersMutations, UsersSubscription
from backend.schemas.home_schema import Form, PositionInput, HomeQuery, HomeMutations

this = sys.modules[__name__]
schema = None


class Query(HomeQuery, UsersQuery, graphene.ObjectType):
    """Combines all schemas queryes"""
    node = relay.Node.Field()
    hello = graphene.String(argument=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, argument):
        """Test function"""
        del info  # not used
        return 'Hello ' + argument


class Mutations(HomeMutations, UsersMutations, graphene.ObjectType):
    """Combines all schemas mutations"""


class Subscription(UsersSubscription, graphene.ObjectType):
    """Combines all schemas subscription"""


def init_schema():
    """Initiate GQL schema"""
    try:
        this.schema = graphene.Schema(
            query=Query,
            mutation=Mutations,
            types=[User, Form, PositionInput],
            subscription=Subscription
        )
    except Exception:
        logger.exception('Error initiating GraphQL shcema. ')
        raise
