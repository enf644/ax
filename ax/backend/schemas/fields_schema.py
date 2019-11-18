""" GQL queries used in fields. For now only AxMessages, AxApproval"""

import uuid
import asyncio
import aiopubsub
import graphene
from loguru import logger
from sqlalchemy.orm import joinedload
import ujson as json
from backend.model import AxMessage, AxMessageThread

import backend.model as ax_model
import backend.misc as ax_misc
import backend.auth as ax_auth
import backend.pubsub as ax_pubsub
# import backend.cache as ax_cache
# import backend.dialects as ax_dialects

from backend.schemas.types import Message
# from backend.auth import ax_admin_only


class CreateMessage(graphene.Mutation):
    """ Creates AxMessage """
    class Arguments:  # pylint: disable=missing-docstring
        thread_guid = graphene.String()
        text = graphene.String()
        data_json = graphene.String(required=False, default_value=None)
        parent = graphene.String(required=False, default_value=None)

    ok = graphene.Boolean()
    message = graphene.Field(Message)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - fields_schema -> CreateMessage.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            thread_guid = args.get('thread_guid')
            text = args.get('text')
            data_json = args.get('data_json')
            current_user = info.context['user']
            user_guid = current_user.get('user_id', None)
            user_email = current_user.get('email', None)
            parent = args.get('parent')

            data = None
            if data_json:
                try:
                    data = json.loads(data_json)
                except ValueError:
                    logger.exception(
                        'Error decoding data_json on creating AxMessage')

            thread = db_session.query(AxMessageThread).filter(
                AxMessageThread.guid == uuid.UUID(args.get('thread_guid'))
            ).first()
            if not thread:
                thread = AxMessageThread()
                thread.guid = uuid.UUID(thread_guid)
                db_session.add(thread)
                db_session.flush()

            new_message = AxMessage()
            new_message.author_guid = ax_misc.guid_or_none(user_guid)
            new_message.author_email = user_email
            new_message.text = text
            new_message.data_json = data
            new_message.thread_guid = thread.guid
            new_message.parent = ax_misc.guid_or_none(parent)

            db_session.add(new_message)
            db_session.flush()

            created_message = db_session.query(AxMessage).filter(
                AxMessage.guid == new_message.guid
            ).options(joinedload(AxMessage.author)).first()

            # joinedload(Event.user)

            db_session.expunge(created_message)
            db_session.expunge(created_message.author)
            ax_pubsub.publisher.publish(
                aiopubsub.Key('thread_message'), {
                    "thread_guid": str(created_message.thread_guid),
                    "ax_message": created_message
                })

            return CreateMessage(message=new_message, ok=True)


class FieldsSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""

    thread_notify = graphene.Field(
        Message,
        thread_guid=graphene.Argument(type=graphene.String, required=True))

    async def resolve_thread_notify(self, info, thread_guid):
        """ Web-socket subscription on new messages in thread """
        try:
            del info
            subscriber = aiopubsub.Subscriber(
                ax_pubsub.hub, 'message_notify_subscriber')
            subscriber.subscribe(aiopubsub.Key('thread_message'))
            while True:
                key, payload = await subscriber.consume()
                await asyncio.sleep(0.1)
                del key
                if payload['thread_guid'] == thread_guid:
                    ax_message = payload['ax_message']
                    yield ax_message
        except asyncio.CancelledError:
            await subscriber.remove_all_listeners()
        except Exception:  # pylint: disable=broad-except
            logger.exception('Error in gql sub resolve_thread_notify.')


class FieldsQuery(graphene.ObjectType):
    """AxFields queryes"""
    thread_messages = graphene.List(
        Message,
        thread_guid=graphene.Argument(type=graphene.String),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )

    async def resolve_thread_messages(
            self, info, thread_guid, update_time=None):
        """Get all AxMessages for specific thread. """
        del update_time
        err = 'Error in GQL query - all_users.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            current_user = info.context['user']

            if not thread_guid:
                return None

            # get thead
            thread = db_session.query(AxMessageThread).filter(
                AxMessageThread.guid == uuid.UUID(thread_guid)
            ).first()

            if not thread:
                return None

            # check field row permission
            perm = True
            if thread.field_guid and thread.row_guid:
                perm = await ax_auth.check_field_perm(
                    db_session=db_session,
                    current_user=current_user,
                    field_guid=thread.field_guid,
                    row_guid=thread.row_guid)

            if not perm:
                return None

            # get messages
            messages = thread.messages
            return messages


class FieldsMutations(graphene.ObjectType):
    """Contains all mutations"""
    create_message = CreateMessage.Field()
