"""Defines Users Scheme and all mutations"""

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from sqlalchemy_utils import UUIDType
from backend.misc import convert_column_to_string
from backend.model import db_session, AxUser
import asyncio
# from rx import Observable


convert_sqlalchemy_type.register(UUIDType)(convert_column_to_string)


class AsyncioPubsub:

    def __init__(self):
        self.subscriptions = {}
        self.sub_id = 0

    async def publish(self, channel, payload):
        if channel in self.subscriptions:
            for q in self.subscriptions[channel].values():
                await q.put(payload)

    def subscribe_to_channel(self, channel):
        self.sub_id += 1
        q = asyncio.Queue()
        if channel in self.subscriptions:
            self.subscriptions[channel][self.sub_id] = q
        else:
            self.subscriptions[channel] = {self.sub_id: q}
        return self.sub_id, q

    def unsubscribe(self, channel, sub_id):
        if sub_id in self.subscriptions.get(channel, {}):
            del self.subscriptions[channel][sub_id]
        if not self.subscriptions[channel]:
            del self.subscriptions[channel]


pubsub = AsyncioPubsub()


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
        await pubsub.publish('BASE', input_text)
        return CreateUser(user=new_user, ok=ok)


class MutationExample(graphene.Mutation):
    class Arguments:
        input_text = graphene.String()

    output_text = graphene.String()

    async def mutate(self, info, input_text):
        # publish to the pubsub object before returning mutation
        await pubsub.publish('BASE', input_text)
        return MutationExample(output_text=input_text)


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


class UsersSubscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to):
        for i in range(up_to):
            yield i
            await asyncio.sleep(1.)
        yield up_to

    mutation_example = graphene.String()

    async def resolve_mutation_example(root, info):
        try:
            # pubsub subscribe_to_channel method returns
            # subscription id and an asyncio.Queue
            sub_id, q = pubsub.subscribe_to_channel('BASE')
            while True:
                payload = await q.get()
                yield payload
        except asyncio.CancelledError:
            # unsubscribe subscription id from channel
            # when coroutine is cancelled
            pubsub.unsubscribe('BASE', sub_id)


class UsersMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    create_user = CreateUser.Field()
    change_username = ChangeUsername.Field()
    mutation_example = MutationExample.Field()
