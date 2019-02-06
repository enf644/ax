"""Defines Users Scheme and all mutations"""

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from sqlalchemy_utils import UUIDType
from backend.misc import convert_column_to_string
from backend.model import db_session, AxUser


convert_sqlalchemy_type.register(UUIDType)(convert_column_to_string)


class Users(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxUser
        interfaces = (relay.Node, )


# Used to Create New User
class CreateUser(graphene.Mutation):
    """ Creates AxUser """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        email = graphene.String()
        username = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    def mutate(self, info, **args):  # pylint: disable=missing-docstring
        del info
        user = AxUser(
            name=args.get('name'),
            email=args.get('email'),
            username=args.get('username')
        )
        db_session.add(user)
        db_session.commit()
        ok = True
        return CreateUser(user=user, ok=ok)


# Used to Change Username with Email
class ChangeUsername(graphene.Mutation):
    """Update AxUser"""
    class Arguments:  # pylint: disable=missing-docstring
        username = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, _, args, context, info):   # pylint: disable=missing-docstring
        del info
        query = Users.get_query(context)
        email = args.get('email')
        username = args.get('username')
        user = query.filter(AxUser.email == email).first()
        user.username = username
        db_session.commit()
        ok = True

        return ChangeUsername(user=user, ok=ok)


class UsersQuery(graphene.ObjectType):
    """AxUser queryes"""
    user = SQLAlchemyConnectionField(Users)
    find_user = graphene.Field(lambda: Users, username=graphene.String())
    all_users = SQLAlchemyConnectionField(Users)

    def resolve_find_user(self, args, context, info):
        """default find method"""
        del info
        query = Users.get_query(context)
        username = args.get('username')
        # you can also use and_ with filter()
        # eg: filter(and_(param1, param2)).first()
        return query.filter(AxUser.username == username).first()


class UsersMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    create_user = CreateUser.Field()
    change_username = ChangeUsername.Field()
