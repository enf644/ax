""" This is part of GraphQL schema (Mutaions, Queryes, Subscriptions).
Contains GQL schema for form actions - DoAction, subscribtion, avalible actions
"""
import os
import sys
import uuid
import copy
import asyncio
# import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import graphene
import aiopubsub
from dotmap import DotMap
from loguru import logger
import ujson as json

from backend.model import AxForm, AxAction
import backend.model as ax_model
import backend.dialects as ax_dialects
import backend.pubsub as ax_pubsub
import backend.misc as ax_misc
import backend.scheduler as ax_scheduler

import backend.cache as ax_cache
from backend.schemas.types import Action, Form, ConsoleMessage, \
    ActionNotifyMessage

import backend.fields.Ax1tom as AxFieldAx1tom   # pylint: disable=unused-import
import backend.fields.Ax1tomTable as AxFieldAx1tomTable  # pylint: disable=unused-import
import backend.fields.AxChangelog as AxFieldAxChangelog  # pylint: disable=unused-import
import backend.fields.AxFiles as AxFieldAxFiles  # pylint: disable=unused-import
import backend.fields.AxImageCropDb as AxFieldAxImageCropDb  # pylint: disable=unused-import
import backend.fields.AxNum as AxFieldAxNum  # pylint: disable=unused-import


this = sys.modules[__name__]
action_loop = None


class InterpreterError(Exception):
    """ Class for AxAction python code errors """


class Executor:
    """In most cases, you can just use the 'execute' instance as a
    function, i.e. y = await execute(f, a, b, k=c) => run f(a, b, k=c) in
    the executor, assign result to y. The defaults can be changed, though,
    with your own instantiation of Executor, i.e. execute =
    Executor(nthreads=4)"""

    def __init__(self, loop, nthreads=1):
        self._ex = ThreadPoolExecutor(nthreads)
        self._loop = loop

    def __call__(self, func, *args, **kw):
        result = self._loop.run_in_executor(
            self._ex, partial(func, *args, **kw))
        return result



async def console_log(msg, modal_guid):
    """ Method used in AxAction terminal. It sends message to vue via ws """
    ax_pubsub.publisher.publish(
        aiopubsub.Key('console_log'),
        {
            'text': msg,
            'modal_guid': modal_guid
        })
    await asyncio.sleep(0.01)


class ConsoleSender:
    """ Used to send ax_console web socket messages to AxForm"""
    def __init__(self, modal_guid):
        self.modal_guid = modal_guid

    def __call__(self, msg):
        console_func = partial(console_log, msg=msg, modal_guid=self.modal_guid)
        this.action_loop.call_soon_threadsafe(console_func)
        asyncio.ensure_future(console_log(msg=msg, modal_guid=self.modal_guid),
                              loop=this.action_loop)


class ActionExecuter:
    """ Runs execute_action with pre-set db_session """
    def __init__(self, db_session):
        self.db_session = db_session

    def __call__(
            self,
            row_guid=None,
            form_guid=None,
            form_db_name=None,
            action_guid=None,
            action_db_name=None,
            values=None,
            modal_guid=None,
            arguments=None):
        return this.execute_action(
            db_session=self.db_session,
            row_guid=row_guid,
            form_guid=form_guid,
            form_db_name=form_db_name,
            action_guid=action_guid,
            action_db_name=action_db_name,
            values=values,
            modal_guid=modal_guid,
            arguments=arguments
        )


async def get_actions(form, current_state=None):
    """ Get actions for current state

    Args:
        form (AxForm): Current form
        current_state (str, optional): Name of current state.
            If None, than it is create action. Defaults to None.

    Returns:
        List(AxAction): List of avalible actions for current form and state
    """
    # TODO: Permissions filter actions, filter fields based on state and user
    ret_actions = []
    state_guid = None
    all_state_guid = None

    for state in form.states:
        if current_state:
            if state.name == current_state:
                state_guid = state.guid
        else:
            if state.is_start:
                state_guid = state.guid
        if state.is_all:
            all_state_guid = state.guid

    for action in form.actions:
        if action.from_state_guid == state_guid:
            ret_actions.append(action)
        if current_state and action.from_state_guid == all_state_guid:
            ret_actions.append(action)
    return ret_actions


async def aexec(code, localz, **kwargs):
    """ This function wraps python code from AxAction with async function
    and runs it """
    # Restore globals later
    args = ", ".join(list(kwargs.keys()))
    code_from_action = code.replace("\n", "\n    ")
    async_code = (f"async def func({args}):"
                  f"\n    {code_from_action}"
                  f"\n    return ax")
    exec(async_code, {}, localz)    # pylint: disable=exec-used
    # Don't expect it to return from the coro.
    result = await localz["func"](**kwargs)
    return result



async def do_exec(db_session, action, form, arguments=None, modal_guid=None):
    """ Executes python commands form AxAction.code

    Args:
        action (AxAction): Current action that is performed
        form (AxForm): Tobe form. Its same as action.form, but it contains
            values from vue form
        arguments(**kargs): Custom dict that can be used in code
        modal_guid (str): AxForm modal guid for wss console subscribtion

    Returns:
        Dict: Its custom Dict containing:
            info (str): Message that must be displayed to user
            error (str): Error that must be displayed to user
            item (DotMap): Javascript style dictionary of field and values.
                example- item.guid -> guid of current row
            exception (Dict): Info on exception that accured
            abort (Bool): If set to True - the action will be aborted and row
                state will not be changed
    """
    import backend.schema as ax_schema

    # async def console_print(msg):
    #     ax_pubsub.publisher.publish(
    #         aiopubsub.Key('console_log'),
    #         {
    #             'text': msg,
    #             'modal_guid': modal_guid
    #         })
    #     await asyncio.sleep(1)

    localz = dict()
    ax = DotMap()  # javascript style dicts item['guid'] == item.guid
    ax.row.guid = form.row_guid
    ax.arguments = arguments
    ax.form = form
    ax.action = action
    ax.schema = ax_schema.schema
    ax.sql = ax_dialects.dialect.custom_query
    ax.print = ConsoleSender(modal_guid=modal_guid)
    ax.paths.uploads = ax_misc.uploads_root_dir
    ax.paths.tmp = ax_misc.tmp_root_dir
    ax.add_action_job = ax_scheduler.add_action_job
    ax.do_action = ActionExecuter(db_session=db_session)
    ax.modal_guid = modal_guid
    for field in form.db_fields:
        ax.row[field.db_name] = field.value
    localz['ax'] = ax
    line_number = None

    try:
        # exec(str(action.code), globals(), localz)   # pylint: disable=exec-used
        # await eval('exec(str(action.code), globals(), localz)')
        ret_ax = await aexec(code=str(action.code), localz=localz, ax=ax)
        ret_ax = localz['ax']

        ret_data = {
            "info": ret_ax.message if 'message' in ret_ax else None,
            "error": ret_ax.error if 'error' in ret_ax else None,
            "item": ret_ax.row,
            "exception": None,
            "abort": ret_ax.abort if 'abort' in ret_ax else None
        }
        return ret_data
    except SyntaxError as err:
        logger.error(err)
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
        ret_data = {
            "info": None,
            "item": None,
            "error": None,
            "exception": {
                "error_class": error_class,
                "line_number": line_number,
                "action_name": action.name,
                "detail": detail
            },
            "abort": True
        }
        return ret_data
    except Exception as err:    # pylint: disable=broad-except
        logger.error(err)
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        del cl, exc
        # line_number = traceback.extract_tb(tb)[-1][1]
        line_number = 0
        traces = traceback.extract_tb(tb)
        for idx, trace in enumerate(traces):
            if trace.filename == '<string>':
                line_number = traceback.extract_tb(tb)[idx].lineno
        del tb

        ret_data = {
            "info": None,
            "item": None,
            "error": None,
            "exception": {
                "error_class": error_class,
                "line_number": line_number,
                "action_name": action.name,
                "detail": detail
            },
            "abort": True
        }
        return ret_data


async def get_before_form(db_session, row_guid, form, ax_action):
    """Constructs before_form AxForm object and populate fields with
    values of specific row. AxForm.fields[0].value

    Args:
        row_guid (str): guid of specific row
        form (AxForm): empty AxForm
        ax_action (AxAction): AxAction wich is currently happening

    Returns:
       before_object (AxForm), tobe_object(AxForm): before_object is AxForm
       with field values of specific row. tobe_row is dummy for future
       population"""
    tobe_form = form

    if row_guid:
        fields_names = [field for field in tobe_form.db_fields]
        before_result = await ax_dialects.dialect.select_one(
            db_session=db_session,
            form=tobe_form,
            fields_list=fields_names,
            row_guid=row_guid)

        if not before_result:
            raise Exception(
                'Error in DoAction. Cant find row for action')

        tobe_form.current_state_name = before_result[0]['axState']
        tobe_form.row_guid = before_result[0]['guid']

        if tobe_form.current_state_name != ax_action.from_state.name \
                and ax_action.from_state.is_all is False:
            raise Exception('Error in DoAction. Performed \
            action does not fit axState')

        # populate each AxField of before_form with old data
        for field in tobe_form.db_fields:
            if field.db_name in before_result[0].keys():
                field.value = before_result[0][field.db_name]
                if (field.value and isinstance(field.value, str) and
                        field.field_type.value_type == 'JSON'):
                    field.value = json.loads(field.value)

    before_form = copy.deepcopy(tobe_form)
    return before_form, tobe_form


async def run_field_backend(db_session, field, action, before_form, tobe_form,
                            current_user, when='before', query_type='update'):
    """Some field types need backend execution on insert/update/delete

    Args:
        field (AxField): contains current .value of updated field
        action (AxAction): Just for info
        before_form (AxForm): Just for info
        tobe_form (AxForm): Just for info
        current_user (AxUser): Just for info
        when (str, optional): Can be 'before' or 'after'.
        query_type (str, optional): Can be 'insert', 'update', 'delete'.
        Defaults to 'update'.

    Returns:
        object: Returns new field value
    """
    tag = field.field_type.tag
    field_py_file_path = f"backend/fields/{tag}.py"
    function_name = f"{when}_{query_type}"

    if os.path.exists(ax_misc.path(field_py_file_path)):
        field_py = globals()[f'AxField{tag}']
        if field_py and hasattr(field_py, function_name):
            method_to_call = getattr(field_py, function_name)
            new_value = await method_to_call(
                db_session=db_session,
                field=field,
                before_form=before_form,
                tobe_form=tobe_form,
                action=action,
                current_user=current_user)
            return new_value
    return field.value


async def execute_action(
        db_session,
        row_guid=None,
        form_guid=None,
        form_db_name=None,
        action_guid=None,
        action_db_name=None,
        values=None,
        modal_guid=None,
        arguments=None):
    """ Performs Action on row
        # 0. Get AxForm
        # 1. Get AxAction and query_type
        # 2. Get before_form - fill it with values from database row
        # 3. Assemble tobe_object - fill it with values from AxForm.vue
        # 4. Run before backend code for each field.
            FieldType can have backend code wich is performed before and after
            action. Sea backend.fields for more info.
        # 5. Run python action, rewrite tobe_object
        # 6. Make update or insert or delete query. Db commit is here.
        # 7. Run after backend code for each field.
        # 8. Fire all web-socket subscribtions. Notify of action performed
            AxForm.vue will display message, that current row have been modified
            AxGrid.vue will reload data of grid

    Args:
        row_guid (str): Guid of row that is opened
        form_guid (str): Guid of AxForm that is opened
        form_db_name (str): db_name of AxForm that is opened.
            (Form guid or db_name must be specified)
        action_guid (str): Guid of AxAction that is performed
        action_db_name (str): db_name of AxAction
            (Action guid or db_name must be specified)
        values (Dict): Dict from AxForm.vue with values of form
        modal_guid (str): Guid generated by AxForm.vue. It used in web-socket
            subscribtion. If current form is performing this action - it does
            not need to notify user of performed action

    Returns:
        form (AxForm): Form that is changed by action. The field values could
            have been changed, if row is created - the row_guid is changed,
            state of current row changed.
        new_guid (str): Guid of current row. Null if row deleted
        messages (Dict): Custom dict containing messages, errors, exceptions
            from executing python code of action. Sea do_exec func for info.
        modal_guid (str): Same as Args. It used in web-socket
            subscribtion. If current form is performing this action - it does
            not need to notify user of performed action
        ok (bool): Used in gql query
    """
    try:
        err = 'action_schema -> execute_action'
        with ax_model.try_catch(db_session, err) as db_session:
            new_guid = uuid.uuid4()
            if not values:
                values = {}
            current_user = None  # TODO: implement users

            # Check if row locked, if not -> lock it
            if row_guid:
                lock_key = f'lock_{row_guid}'
                is_locked = await ax_cache.cache.get(lock_key)
                if not is_locked:
                    await ax_cache.cache.set(lock_key, True)
                else:
                    messages = {
                        "exception": None,
                        "error": "$i18n('form.row-locked')",
                        "info": None
                    }
                    messages_json = json.dumps(messages)
                    return {
                        "form": None,
                        "new_guid": None,
                        "messages": messages_json,
                        "modal_guid": modal_guid,
                        "ok": False
                    }

            # 0. Get AxForm
            ax_form = None
            if form_guid:
                ax_form = db_session.query(AxForm).filter(
                    AxForm.guid == uuid.UUID(form_guid)
                ).first()
            elif form_db_name:
                ax_form = db_session.query(AxForm).filter(
                    AxForm.db_name == form_db_name
                ).first()
            else:
                raise ValueError(
                    'doAction GQL - form guid or db_name required')

            db_session.expire(ax_form)

            # 1. Get AxAction and query_type
            ax_action = None
            if not action_guid and not action_db_name:
                raise ValueError(
                    'doAction GQL - action guid or db_name required')
            for action in ax_form.actions:
                if not ax_action:
                    if action_guid and action.guid == uuid.UUID(action_guid):
                        ax_action = action
                    if action_db_name and action.db_name == action_db_name:
                        ax_action = action

            query_type = 'update'
            if ax_action.from_state.is_start:
                query_type = 'insert'
            elif ax_action.to_state.is_deleted:
                query_type = 'delete'

            # 2. Get before_form - fill it with values from database row
            before_form, tobe_form = await get_before_form(
                db_session=db_session,
                row_guid=row_guid,
                form=ax_form,
                ax_action=ax_action)

            # 3. Assemble tobe_object - fill it with values from AxForm.vue
            if not tobe_form.row_guid:
                tobe_form.row_guid = new_guid
            for field in tobe_form.db_fields:
                if field.db_name in values.keys():
                    field.value = values[field.db_name]
                    field.needs_sql_update = True
                if field.field_type.is_updated_always:
                    field.needs_sql_update = True

            # 4. Run before backend code for each field.
            for field in tobe_form.no_tab_fields:
                if field.field_type.is_backend_available:
                    field.value = await run_field_backend(
                        db_session=db_session,
                        when='before',
                        query_type=query_type,
                        field=field,
                        action=ax_action,
                        before_form=before_form,
                        tobe_form=tobe_form,
                        current_user=current_user)

            # 5. Run python action, rewrite tobe_object
            messages = None
            messages_json = None
            if ax_action.code:
                code_result = await do_exec(
                    db_session=db_session,
                    action=ax_action,
                    form=tobe_form,
                    arguments=arguments,
                    modal_guid=modal_guid)
                messages = {
                    "exception": code_result["exception"],
                    "error": code_result["error"],
                    "info": code_result["info"]
                }
                messages_json = json.dumps(messages)
                if code_result['abort'] or code_result["exception"]:
                    await ax_cache.cache.delete(f'lock_{row_guid}')
                    return {
                        "form": before_form,
                        "new_guid": None,
                        "messages": messages_json,
                        "modal_guid": modal_guid,
                        "ok": False
                    }
                # update fields with values recieved from actions python
                new_item = code_result['item']
                for field in tobe_form.db_fields:
                    if field.db_name in new_item.keys():
                        field.value = new_item[field.db_name]
                        field.needs_sql_update = True

            # 6. Make update or insert or delete query #COMMIT HERE
            return_guid = tobe_form.row_guid
            after_form = copy.deepcopy(tobe_form)
            if query_type == 'insert':
                await ax_dialects.dialect.insert(
                    db_session=db_session,
                    form=tobe_form,
                    to_state_name=ax_action.to_state.name,
                    new_guid=new_guid
                )
                tobe_form.row_guid = new_guid
                return_guid = new_guid
            elif query_type == 'delete':
                await ax_dialects.dialect.delete(
                    db_session=db_session,
                    form=tobe_form,
                    row_guid=tobe_form.row_guid
                )
                return_guid = None
            else:
                await ax_dialects.dialect.update(
                    db_session=db_session,
                    form=tobe_form,
                    to_state_name=ax_action.to_state.name,
                    row_guid=tobe_form.row_guid
                )

            # 7. Run after backend code for each field.
            for field in after_form.no_tab_fields:
                if field.field_type.is_backend_available:
                    field.value = await run_field_backend(
                        db_session=db_session,
                        when='after',
                        query_type=query_type,
                        field=field,
                        action=ax_action,
                        before_form=before_form,
                        tobe_form=after_form,
                        current_user=current_user)

            # 8. Fire all web-socket subscribtions. Notify of action performed
            # subscription_form = AxForm()
            # subscription_form.guid = tobe_form.guid
            # subscription_form.icon = tobe_form.icon
            # subscription_form.db_name = tobe_form.db_name
            # subscription_form.row_guid = tobe_form.row_guid
            # subscription_form.modal_guid = modal_guid

            notify_message = {
                "form_guid": tobe_form.guid,
                "form_icon": tobe_form.icon,
                "form_db_name": tobe_form.db_name,
                "row_guid": tobe_form.row_guid,
                "modal_guid": modal_guid,
                "action_guid": ax_action.guid,
                "action_db_name": ax_action.db_name,
                "action_icon": ax_action.icon
            }

            ax_pubsub.publisher.publish(
                aiopubsub.Key('do_action'), notify_message)

            await ax_cache.cache.delete(f'lock_{row_guid}')
            return {
                "form": tobe_form,
                "new_guid": return_guid,
                "messages": messages_json,
                "modal_guid": modal_guid,
                "ok": True
            }
    except Exception:
        await ax_cache.cache.delete(f'lock_{row_guid}')
        logger.exception('Error while executing action - DoAction.')
        raise


def run_async(corofn, *args):
    """  run_in_executor takes only sync function, but with
    this hack we can run corutines """
    loop = asyncio.new_event_loop()
    coro = corofn(*args)
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def run_execute_action(
        db_session,
        row_guid=None,
        form_guid=None,
        form_db_name=None,
        action_guid=None,
        action_db_name=None,
        values=None,
        modal_guid=None,
        arguments=None
    ):
    """ This function executes execute_action corutine in different thread """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=5)
    execute_func = partial(
        execute_action,
        db_session=db_session,
        row_guid=row_guid,
        form_guid=form_guid,
        form_db_name=form_db_name,
        action_guid=action_guid,
        action_db_name=action_db_name,
        values=values,
        modal_guid=modal_guid,
        arguments=arguments
    )

    result = await loop.run_in_executor(
        executor,
        run_async,
        execute_func)

    return result




class DoAction(graphene.Mutation):
    """
        Runs execute_action. Performs action on row.
    """
    class Arguments:  # pylint: disable=missing-docstring
        row_guid = graphene.String(required=False, default_value=None)
        form_guid = graphene.String(required=False, default_value=None)
        form_db_name = graphene.String(required=False, default_value=None)
        action_guid = graphene.String(required=False, default_value=None)
        action_db_name = graphene.String(required=False, default_value=None)
        values = graphene.String()
        arguments = graphene.String(required=False, default_value=None)
        modal_guid = graphene.String(required=False, default_value=None)

    form = graphene.Field(Form)
    new_guid = graphene.String()
    messages = graphene.String()
    modal_guid = graphene.String()
    ok = graphene.Boolean()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - action_schema -> DoAction.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            values_string = args.get('values')
            values = {}
            if values_string and values_string != 'null':
                values = json.loads(values_string)
            row_guid = args.get('row_guid')
            modal_guid = args.get('modal_guid')
            form_guid = args.get('form_guid')
            form_db_name = args.get('form_db_name')
            action_guid = args.get('action_guid')
            action_db_name = args.get('action_db_name')
            arguments_string = args.get('arguments')
            arguments = {}
            if arguments_string and arguments_string != 'null':
                arguments = json.loads(arguments_string)

            result = await run_execute_action(
                db_session=db_session,
                row_guid=row_guid,
                form_guid=form_guid,
                form_db_name=form_db_name,
                action_guid=action_guid,
                action_db_name=action_db_name,
                values=values,
                arguments=arguments,
                modal_guid=modal_guid)

            return DoAction(
                form=result["form"],
                new_guid=result["new_guid"],
                messages=result["messages"],
                modal_guid=result["modal_guid"],
                ok=result["ok"])


class ActionSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""
    action_notify = graphene.Field(
        ActionNotifyMessage,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        row_guid=graphene.Argument(type=graphene.String, required=False))

    async def resolve_action_notify(self, info, form_db_name, row_guid=None):
        """ Web-socket subscription on every performed action
            AxForm.vue will display message, that current row have been modified
            AxGrid.vue will reload data of grid

            Args:
                form_db_name (str): db_name of AxForm
                row_guid (str): If it is set, then the subscriber will be
                    notified only on actions performed with surtain row.
                    AxGrid is notified on every action
                    AxForm is notified only on row actions

            Returns:
                payload (Dict): Dict containing action info:
                    form_guid (str): AxForm.guid of current form
                    form_icon (str): font-awesome icon
                    form_db_name (str): AxForm.db_name of current form
                    row_guid (str): Guid of row on wich action is performed
                    modal_guid (str): Guid generated by AxForm.vue.
                        It used in web-socket subscribtion. If current form is
                        performing this action - it doesnot need to notify user
                        of performed action
                    action_guid (str): Current action guid
                    action_db_name (str): Db name of current action
                    action_icon (str): font-awesome icon of current action

        """
        try:
            del info
            subscriber = aiopubsub.Subscriber(
                ax_pubsub.hub, 'action_notify_subscriber')
            subscriber.subscribe(aiopubsub.Key('do_action'))
            while True:
                key, payload = await subscriber.consume()
                del key
                if payload['form_db_name'] == form_db_name:
                    if row_guid is None or row_guid == payload['row_guid']:
                        message = ActionNotifyMessage(
                            form_guid=payload['form_guid'],
                            form_icon=payload['form_icon'],
                            form_db_name=payload['form_db_name'],
                            row_guid=payload['row_guid'],
                            modal_guid=payload['modal_guid'],
                            action_guid=payload['action_guid'],
                            action_db_name=payload['action_db_name'],
                            action_icon=payload['action_icon'])
                        yield message
        except asyncio.CancelledError:
            await subscriber.remove_all_listeners()


    console_notify = graphene.Field(
        ConsoleMessage,
        modal_guid=graphene.Argument(type=graphene.String, required=True))

    async def resolve_console_notify(self, info, modal_guid):
        """ Web-socket subscription on ax terminal print
        """
        try:
            del info
            subscriber = aiopubsub.Subscriber(
                ax_pubsub.hub, 'action_notify_subscriber')
            subscriber.subscribe(aiopubsub.Key('console_log'))
            this.action_loop = asyncio.get_event_loop()
            while True:
                key, payload = await subscriber.consume()
                await asyncio.sleep(0.1)
                del key
                if payload['modal_guid'] == modal_guid:
                    message = ConsoleMessage(
                        text=payload['text'],
                        modal_guid=payload['modal_guid'])
                    yield message
        except asyncio.CancelledError:
            await subscriber.remove_all_listeners()
        except Exception: # pylint: disable=broad-except
            logger.exception('Error in gql sub resolve_console_notify.')



class ActionQuery(graphene.ObjectType):
    """Query all data of AxAction and related classes"""
    action_data = graphene.Field(
        Action,
        guid=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False))
    actions_avalible = graphene.List(
        Action,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        current_state=graphene.Argument(type=graphene.String, required=False),
        update_time=graphene.Argument(type=graphene.String, required=False))

    async def resolve_action_data(self, info, guid=None, update_time=None):
        """ Gets AxAction by guid. Used in TheActionModal.vue. """
        del update_time
        err = 'action_schema -> resolve_action_data'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            query = Action.get_query(info=info)
            ax_action = query.filter(AxAction.guid == uuid.UUID(guid)).first()
            return ax_action

    async def resolve_actions_avalible(self, info, form_db_name,
                                       current_state=None, update_time=None):
        """ Gets AxActions for current state """
        # TODO: Add permissions based on roles and current user
        del update_time
        err = (f"action_schema.resolve_actions_avalible."
               f"Error in gql query - resolve_actions_avalible.")
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True) as db_session:
            ax_form = db_session.query(AxForm).filter(
                AxForm.db_name == form_db_name
            ).first()
            ax_actions = await get_actions(
                form=ax_form, current_state=current_state)

            return ax_actions



class ActionMutations(graphene.ObjectType):
    """Combine all mutations"""
    do_action = DoAction.Field()
