"""Ax GraphQL schema
Combines all Ax GraphQL schemas to one
"""
import sys
import graphene
from loguru import logger
from graphene_sqlalchemy import SQLAlchemyConnectionField
from backend.schemas.users_schema import UsersQuery
from backend.schemas.users_schema import UsersMutations, UsersSubscription
from backend.schemas.home_schema import HomeQuery, HomeMutations
from backend.schemas.form_schema import FormQuery, FormMutations
from backend.schemas.grids_schema import GridsQuery, GridsMutations
from backend.schemas.types import Form, FieldType, Field, Grid, \
    Column, User, Role, State, Action, RoleFieldPermission, PositionInput

from backend.model import AxForm
import backend.model as ax_model

this = sys.modules[__name__]
schema = None


type_dictionary = {
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

gql_types = [
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
]


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


class Mutations(HomeMutations, FormMutations, UsersMutations, GridsMutations,
                graphene.ObjectType):
    """Combines all schemas mutations"""


class Subscription(UsersSubscription, graphene.ObjectType):
    """Combines all schemas subscription"""


def make_resolver(db_name, type_class):
    """ Dynamicly create resolver for GrapQL query based on """

    def resolver(self, info):
        del self, info
        result_items = []
        sql = f'SELECT * FROM {db_name}'
        results = ax_model.db_session.execute(sql).fetchall()
        for row in results:
            kwargs = {}
            for key, value in row.items():
                kwargs[key] = value

            result_items.append(type_class(**kwargs))

        return result_items
    resolver.__name__ = 'resolve_%s' % db_name
    return resolver


def init_schema():
    """Initiate GQL schema"""
    try:
        # Create typeClass based on each AxForm
        type_classes = {}
        ax_forms = ax_model.db_session.query(AxForm).all()
        for form in ax_forms:
            class_name = form.db_name.capitalize()
            class_fields = {}
            class_fields['guid'] = graphene.String()
            for field in form.db_fields:
                field_type = type_dictionary[field.field_type.value_type]
                # TODO maybe add label as description?
                class_fields[field.db_name] = field_type()

            graph_class = type(
                class_name,
                (graphene.ObjectType,),
                class_fields,
                name=form.db_name,
                description=form.name
            )
            type_classes[form.db_name] = graph_class
            gql_types.append(graph_class)

        # Dynamicly crate resolvers for each typeClass
        dynamic_fields = {}
        for key, type_class in type_classes.items():
            dynamic_fields[key] = graphene.List(type_class)
            dynamic_fields['resolve_%s' % key] = make_resolver(key, type_class)

        DynamicQuery = type('DynamicQuery', (Query,), dynamic_fields)

        this.schema = graphene.Schema(
            query=DynamicQuery,
            mutation=Mutations,
            types=gql_types,
            subscription=Subscription
        )
    except Exception:
        logger.exception('Error initiating GraphQL shcema. ')
        raise
