
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from backend.model import AxForm, AxField, AxFieldType, AxGrid, AxColumn, AxUser, AxRole, AxState, AxAction, AxRoleFieldPermission, GUID  # TODO check if needed
from backend.misc import convert_column_to_string

convert_sqlalchemy_type.register(GUID)(convert_column_to_string)


class Form(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxForm
        interfaces = (relay.Node, )


class FieldType(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxFieldType
        interfaces = (relay.Node, )


class PositionInput(graphene.InputObjectType):
    """Used to store position data"""
    guid = graphene.NonNull(graphene.String)
    position = graphene.NonNull(graphene.Int)
    parent = graphene.NonNull(graphene.String)


class Field(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxField
        interfaces = (relay.Node, )


class Grid(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxGrid
        interfaces = (relay.Node, )


class Column(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxColumn
        interfaces = (relay.Node, )


class User(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxUser
        interfaces = (relay.Node, )


class Role(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxRole
        interfaces = (relay.Node, )


class State(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxState
        interfaces = (relay.Node, )


class Action(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxAction
        interfaces = (relay.Node, )


class RoleFieldPermission(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxRoleFieldPermission
        interfaces = (relay.Node, )
