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


TypeDictionary = {
    'text': graphene.String,
    'TEXT': graphene.String,
    'VARCHAR(255)': graphene.String,
    'INT': graphene.Int,
    'DECIMAL(65,2)': graphene.Float,
    'BOOL': graphene.Boolean,
    'GUID': graphene.String,
    'JSON': graphene.String,
    'TIMESTAMP': graphene.Int,
    'BLOB': graphene.String
}

# class MyType1(graphene.ObjectType):
#     name = graphene.String()
MyType1 = type('MyType1', (graphene.ObjectType,), {
    'name': graphene.String(),
})

# Create types dict
# Create typeClass based on each AxForm
# Dynamicly crate resolvers for each typeClass
# Dynamicly add queriy and resolve_ for each AxForm


def make_resolver(record_name, record_class):
    def resolver(self, info):
        return record_class(name='Hello world')
    resolver.__name__ = 'resolve_%s' % record_name
    return resolver


# class MyQuery1(graphene.ObjectType):
#     some = graphene.Field(MyType1)


#     def resolve_some(self, info):
#         return MyType1(name='Hello world')
# MyQuery1 = type('Query', (graphene.ObjectType,), {
#     'some': graphene.Field(MyType1),
#     'resolve_some': make_resolver('some', MyType1)
# })


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

    DynamicQuery = type('DynamicQuery', (Query,), {
        'some': graphene.Field(MyType1),
        'resolve_some': make_resolver('some', MyType1)
    })

    # classname = 'dynamic'
    # fields = {}
    # fields['name'] = graphene.String()

    # dynamic_class = type(
    #     classname,
    #     (graphene.ObjectType,),
    #     fields,
    #     name=record_type['name'],
    #     description=record_type['desc'],
    # )

    try:
        this.schema = graphene.Schema(
            query=DynamicQuery,
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
                PositionInput,
                MyType1
            ],
            subscription=Subscription
        )
    except Exception:
        logger.exception('Error initiating GraphQL shcema. ')
        raise
