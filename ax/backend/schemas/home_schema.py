"""Defines Users Scheme and all mutations"""

import graphene
# from graphene import relay
# from graphene_sqlalchemy import SQLAlchemyConnectionField,SQLAlchemyObjectType
# from graphene_sqlalchemy.converter import convert_sqlalchemy_type
# from sqlalchemy_utils import UUIDType
# from ax.backend.misc import convert_column_to_string
# from ax.backend.model import db_session, AxUser
# from rx import Observable


class HomeQuery(graphene.ObjectType):
    """Test query"""
    is_staff = graphene.Boolean(name='is_staff')

    def resolve_is_staff(self, info):
        """Test method"""
        del info
        return True
