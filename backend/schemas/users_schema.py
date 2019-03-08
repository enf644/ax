"""Defines Users Scheme and all mutations"""

import asyncio
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from sqlalchemy_utils import UUIDType
import aiopubsub

from backend.misc import convert_column_to_string
from backend.model import db_session, AxUser
import backend.cache as ax_cache
import backend.pubsub as ax_pubsub

convert_sqlalchemy_type.register(UUIDType)(convert_column_to_string)


class User(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxUser
        interfaces = (relay.Node, )


class CreateUser(graphene.Mutation):
    """ Creates AxUser """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        email = graphene.String()
        username = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        del info
        new_user = AxUser(
            name=args.get('name'),
            email=args.get('email'),
            username=args.get('username')
        )
        db_session.add(new_user)
        db_session.commit()
        ok = True
        # await simple_bupsub.publish('BASE', new_user)
        ax_pubsub.publisher.publish(aiopubsub.Key('new_user'), new_user)
        return CreateUser(user=new_user, ok=ok)


class MutationExample(graphene.Mutation):
    """Mutation example"""
    class Arguments:  # pylint: disable=missing-docstring
        input_text = graphene.String()

    output_text = graphene.String()

    async def mutate(self, info, input_text):  # pylint: disable=missing-docstring
        del info
        return MutationExample(output_text=input_text)


# Used to Change Username with Email
class ChangeUsername(graphene.Mutation):
    """Update AxUser"""
    class Arguments:  # pylint: disable=missing-docstring
        username = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    @classmethod
    def mutate(cls, _, args, context, info):   # pylint: disable=missing-docstring
        del info
        query = User.get_query(context)
        email = args.get('email')
        username = args.get('username')
        user = query.filter(AxUser.email == email).first()
        user.username = username
        db_session.commit()
        ok = True

        return ChangeUsername(user=user, ok=ok)


class UsersQuery(graphene.ObjectType):
    """AxUser queryes"""
    user = SQLAlchemyConnectionField(User)
    find_user = graphene.Field(lambda: User, username=graphene.String())
    all_users = graphene.List(User)

    async def resolve_all_users(self, info):
        """Get all users"""
        query = User.get_query(info)  # SQLAlchemy query
        user_list = query.all()
        await ax_cache.cache.set('user_list', user_list)
        return user_list

    def resolve_find_user(self, args, context, info):
        """default find method"""
        del info
        query = User.get_query(context)
        username = args.get('username')
        # you can also use and_ with filter()
        # eg: filter(and_(param1, param2)).first()
        return query.filter(AxUser.username == username).first()


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
    change_username = ChangeUsername.Field()
    mutation_example = MutationExample.Field()
