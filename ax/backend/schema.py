"""Ax GraphQL schema
Combines all Ax GraphQL schemas to one
"""
import sys
import graphene
from loguru import logger
from sqlalchemy import literal
from graphene_sqlalchemy import SQLAlchemyConnectionField
import ujson as json
from backend.schemas.users_schema import UsersQuery
from backend.schemas.users_schema import UsersMutations, UsersSubscription
from backend.schemas.home_schema import HomeQuery, HomeMutations
from backend.schemas.form_schema import FormQuery, FormMutations
from backend.schemas.workflow_schema import WorkflowQuery, WorkflowMutations, \
    WorkflowSubscription
from backend.schemas.grids_schema import GridsQuery, GridsMutations
from backend.schemas.fields_schema import FieldsQuery, FieldsMutations
from backend.schemas.types import Form, FieldType, Field, Grid, \
    Column, User, Role, State, Action, RoleFieldPermission, Group2Users, \
    Action2Role, State2Role, Role2Users, PositionInput

from backend.model import AxForm
import backend.model as ax_model
import backend.dialects as ax_dialects


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
    Group2Users,
    Action2Role,
    State2Role,
    Role2Users,
    PositionInput,
]


class Query(HomeQuery, FormQuery, UsersQuery, GridsQuery,
            WorkflowQuery, FieldsQuery, graphene.ObjectType):
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
    group_to_users = SQLAlchemyConnectionField(Group2Users)


class Mutations(HomeMutations, FormMutations, UsersMutations, GridsMutations,
                WorkflowMutations, FieldsMutations, graphene.ObjectType):
    """Combines all schemas mutations"""


class Subscription(UsersSubscription, WorkflowSubscription, graphene.ObjectType):
    """Combines all schemas subscription"""


def make_resolver(db_name, type_class):
    """ Dynamicly create resolver for GrapQL query based on
        db_name - db_name of AxForm + db_name of AxGrid.
        or only db_name of AxForm for default view grid

        Example:
        db_name=MyUberFormGridOne 
        MyUberForm is form name
        GridOne is grid name

    """

    def resolver(self, info, update_time=None, quicksearch=None, guids=None):
        del self, info, update_time

        # Find AxForm with name that db_name is started with
        ax_form = ax_model.db_session.query(AxForm).filter(
            literal(db_name).startswith(AxForm.db_name)
        ).first()

        # iterate all grids to know, what grid to use
        ax_grid = {}
        default_grid = {}
        for grid in ax_form.grids:
            if ax_form.db_name + grid.db_name == db_name:
                ax_grid = grid
            if grid.is_default_view:
                default_grid = grid

        grid_to_use = ax_grid or default_grid
        grid_options = json.loads(grid_to_use.options_json)
        server_filter = None
        if 'serverFilter' in grid_options:
            server_filter = grid_options['serverFilter']

        # TODO add permission checks
        allowed_fields = []
        for field in ax_form.db_fields:
            allowed_fields.append(field.db_name)

        # select * from table
        # TODO Add paging
        results = ax_dialects.dialect.select_all(
            ax_form=ax_form,
            quicksearch=quicksearch,
            server_filter=server_filter,
            guids=guids)

        result_items = []
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
        this.schema = None
        type_classes = {}
        all_types = gql_types.copy()

        ax_forms = ax_model.db_session.query(AxForm).all()
        for form in ax_forms:
            for grid in form.grids:
                # For each grid we create Graphene field with name FormGrid
                capital_form_db_name = form.db_name[0].upper(
                ) + form.db_name[1:]
                class_name = capital_form_db_name + grid.db_name
                class_fields = {}
                class_fields['guid'] = graphene.String()
                class_fields['axNum'] = graphene.Int()
                class_fields['axState'] = graphene.String()
                class_fields['axLabel'] = graphene.String()
                class_fields['axIcon'] = graphene.String()

                # Add fields for each field of AxForm
                for field in form.db_fields:
                    field_type = type_dictionary[field.field_type.value_type]
                    # TODO maybe add label as description?
                    class_fields[field.db_name] = field_type()

                # Create graphene class and append class dict
                graph_class = type(
                    class_name,
                    (graphene.ObjectType,),
                    class_fields,
                    name=class_name,
                    description=form.name
                )
                type_classes[class_name] = graph_class
                all_types.append(graph_class)

                # if grid is default view we add enother class with name Form
                # without Grid name
                if grid.is_default_view is True:
                    default_class_name = form.db_name[0].upper(
                    ) + form.db_name[1:]

                    default_graph_class = type(
                        default_class_name,
                        (graphene.ObjectType,),
                        class_fields,
                        name=default_class_name,
                        description=form.name
                    )
                    type_classes[default_class_name] = graph_class
                    all_types.append(default_graph_class)

        # Dynamicly crate resolvers for each typeClass
        # Iterate throw created classes and create resolver for each
        dynamic_fields = {}
        for key, type_class in type_classes.items():
            dynamic_fields[key] = graphene.List(
                type_class,
                update_time=graphene.Argument(
                    type=graphene.String, required=False),
                quicksearch=graphene.Argument(
                    type=graphene.String, required=False),
                guids=graphene.Argument(
                    type=graphene.String, required=False)
            )

            dynamic_fields['resolve_%s' % key] = make_resolver(key, type_class)

        DynamicQuery = type('DynamicQuery', (Query,), dynamic_fields)

        this.schema = graphene.Schema(
            query=DynamicQuery,
            mutation=Mutations,
            types=all_types,
            subscription=Subscription
        )
    except Exception:
        logger.exception('Error initiating GraphQL shcema. ')
        raise
