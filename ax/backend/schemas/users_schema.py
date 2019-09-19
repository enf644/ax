"""Defines Users Scheme and all mutations"""

# import asyncio
import graphene
# from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
import aiopubsub
# from loguru import logger

from backend.misc import convert_column_to_string
from backend.model import AxUser, GUID
import backend.model as ax_model
# import backend.cache as ax_cache
import backend.pubsub as ax_pubsub
from backend.schemas.types import User

convert_sqlalchemy_type.register(GUID)(convert_column_to_string)


class CreateUser(graphene.Mutation):
    """ Creates AxUser """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> CreateUser.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            new_user = AxUser(
                name=args.get('name'),
                email=args.get('email'),
            )
            db_session.add(new_user)
            db_session.flush()

            ok = True
            ax_pubsub.publisher.publish(aiopubsub.Key('new_user'), new_user)
            return CreateUser(user=new_user, ok=ok)


class MutationExample(graphene.Mutation):
    """Mutation example"""
    class Arguments:  # pylint: disable=missing-docstring
        input_text = graphene.String(required=False, default_value=None)

    output_text = graphene.String()

    def mutate(self, info, input_text=None):  # pylint: disable=missing-docstring
        del info
        ret_text = input_text
        if not input_text:
            ret_text = "default text"
        print('\n\n\n\n!!!' + ret_text + '!!!\n\n\n\n')
        return MutationExample(output_text=ret_text)

# Used to Change Username with Email


class ChangeUserName(graphene.Mutation):
    """Update AxUser"""
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    @classmethod
    def mutate(cls, _, args, context, info):   # pylint: disable=missing-docstring
        err = 'Error in gql - users_schema -> ChangeUserName'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            query = User.get_query(context)
            email = args.get('email')
            name = args.get('name')
            user = query.filter(AxUser.email == email).first()
            user.name = name
            db_session.flush()
            return ChangeUserName(user=user, ok=True)


class UsersQuery(graphene.ObjectType):
    """AxUser queryes"""
    ax_user = SQLAlchemyConnectionField(User)
    find_user = graphene.Field(lambda: User, email=graphene.String())
    all_users = graphene.List(User)

    async def resolve_all_users(self, info):
        """Get all users"""
        err = 'Error in GQL query - all_users.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            query = User.get_query(info)  # SQLAlchemy query
            user_list = query.all()
            return user_list

    def resolve_find_user(self, args, context, info):
        """default find method"""
        err = 'Error in GQL query - find_user.'
        with ax_model.try_catch(info.context['session'], err, no_commit=True):
            del info
            query = User.get_query(context)
            email = args.get('email')
            # you can also use and_ with filter()
            # eg: filter(and_(param1, param2)).first()
            return query.filter(AxUser.email == email).first()


class UsersSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""


class UsersMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    create_user = CreateUser.Field()
    change_username = ChangeUserName.Field()
    mutation_example = MutationExample.Field()
