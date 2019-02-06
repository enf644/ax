"""Axy GraphQL schema
Combines all Axy GraphQL schemas to one
"""

import graphene
from graphene import relay
from backend.schemas.users_schema import UsersQuery, UsersMutations, Users


class Query(UsersQuery, graphene.ObjectType):
    """Combines all schemas queryes"""
    node = relay.Node.Field()
    hello = graphene.String(argument=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, argument):
        """Test function"""
        del info  # not used
        return 'Hello ' + argument


class MyMutations(UsersMutations, graphene.ObjectType):
    """Combines all schemas mutations"""


schema = graphene.Schema(query=Query, mutation=MyMutations, types=[Users])
