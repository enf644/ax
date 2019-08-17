"""Defines Users Scheme and all mutations"""

import asyncio
from sqlalchemy.exc import DatabaseError
import graphene
# from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
import aiopubsub
from loguru import logger

from backend.misc import convert_column_to_string
from backend.model import AxUser, GUID
import backend.model as ax_model
import backend.cache as ax_cache
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
        try:
            del info
            new_user = AxUser(
                name=args.get('name'),
                email=args.get('email'),
            )
            ax_model.db_session.add(new_user)
            try:
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(
                    f"Error executing SQL, rollback! - CreateUser")

            ok = True
            ax_pubsub.publisher.publish(aiopubsub.Key('new_user'), new_user)
            return CreateUser(user=new_user, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateUser.')
            raise


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
        try:
            del info
            query = User.get_query(context)
            email = args.get('email')
            name = args.get('name')
            user = query.filter(AxUser.email == email).first()
            user.name = name
            try:
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(
                    f"Error executing SQL, rollback! - ChangeUserName")

            ok = True
            return ChangeUserName(user=user, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - ChangeUserName.')
            raise


class UsersQuery(graphene.ObjectType):
    """AxUser queryes"""
    user = SQLAlchemyConnectionField(User)
    find_user = graphene.Field(lambda: User, email=graphene.String())
    all_users = graphene.List(User)

    async def resolve_all_users(self, info):
        """Get all users"""
        try:
            query = User.get_query(info)  # SQLAlchemy query
            user_list = query.all()
            await ax_cache.cache.set('user_list', user_list)
            return user_list
        except Exception:
            logger.exception('Error in GQL query - all_users.')
            raise

    def resolve_find_user(self, args, context, info):
        """default find method"""
        try:
            del info
            query = User.get_query(context)
            email = args.get('email')
            # you can also use and_ with filter()
            # eg: filter(and_(param1, param2)).first()
            return query.filter(AxUser.email == email).first()
        except Exception:
            logger.exception('Error in GQL query - find_user.')
            raise


class UsersSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""
    count_seconds = graphene.Float(up_to=graphene.Int())
    mutation_example = graphene.Field(User)
    test_sub = graphene.String()

    async def resolve_count_seconds(self, info, up_to):
        """Test graphql subscription"""
        del info

        for i in range(up_to):
            yield i
            await asyncio.sleep(1.)
        yield up_to

    async def resolve_mutation_example(self, info):
        """Subscribe to adding new user"""
        del info
        try:
            subscriber = aiopubsub.Subscriber(
                ax_pubsub.hub, 'new_user_subscriber')
            subscriber.subscribe(aiopubsub.Key('new_user'))
            while True:
                key, payload = await subscriber.consume()
                del key
                yield payload
        except asyncio.CancelledError:
            await subscriber.remove_all_listeners()


class UsersMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    create_user = CreateUser.Field()
    change_username = ChangeUserName.Field()
    mutation_example = MutationExample.Field()
