"""Ax GraphQL schema
Combines all Ax GraphQL schemas to one
"""
import sys
import graphene
from graphene import relay
from loguru import logger
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from backend.schemas.users_schema import User, UsersQuery
from backend.schemas.users_schema import UsersMutations, UsersSubscription
from backend.schemas.home_schema import HomeQuery, HomeMutations
from backend.schemas.form_schema import FormQuery, FormMutations
from backend.schemas.grids_schema import GridsQuery, GridsMutations
from backend.schemas.types import Form, FieldType, Field, Grid, Column, User, Role, State, Action, RoleFieldPermission, PositionInput

this = sys.modules[__name__]
schema = None


class Query(HomeQuery, FormQuery, UsersQuery, GridsQuery, graphene.ObjectType):
    """Combines all schemas queryes"""
    forms = SQLAlchemyConnectionField(Form)
    field_types = SQLAlchemyConnectionField(FieldType)
    fields = SQLAlchemyConnectionField(Field)
    grids = SQLAlchemyConnectionField(Grid)
    columns = SQLAlchemyConnectionField(Column)
    users = SQLAlchemyConnectionField(User)
    roles = SQLAlchemyConnectionField(Role)
    states = SQLAlchemyConnectionField(State)
    actions = SQLAlchemyConnectionField(Action)
    role_field_permissions = SQLAlchemyConnectionField(RoleFieldPermission)


class Mutations(HomeMutations, FormMutations, UsersMutations, GridsMutations, graphene.ObjectType):
    """Combines all schemas mutations"""


class Subscription(UsersSubscription, graphene.ObjectType):
    """Combines all schemas subscription"""


def init_schema():
    """Initiate GQL schema"""
    try:
        this.schema = graphene.Schema(
            query=Query,
            mutation=Mutations,
            types=[
                Form,
                FieldType,
                Field,
                Grid,
                Column,
                User,
                Role,
                State,
                Action,
                RoleFieldPermission,
                PositionInput
            ],
            subscription=Subscription
        )
    except Exception:
        logger.exception('Error initiating GraphQL shcema. ')
        raise
