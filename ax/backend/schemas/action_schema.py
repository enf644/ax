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
import graphene
import aiopubsub
from dotmap import DotMap
from loguru import logger
import ujson as json

from backend.model import AxForm, AxAction
import backend.model as ax_model
import backend.dialects as ax_dialects
import backend.pubsub as ax_pubsub
import backend.schema as ax_schema
import backend.misc as ax_misc
import backend.scheduler as ax_scheduler

# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import Action, Form

import backend.fields.Ax1tom as AxFieldAx1tom   # pylint: disable=unused-import
import backend.fields.Ax1tomTable as AxFieldAx1tomTable  # pylint: disable=unused-import
import backend.fields.AxChangelog as AxFieldAxChangelog  # pylint: disable=unused-import
import backend.fields.AxFiles as AxFieldAxFiles  # pylint: disable=unused-import
import backend.fields.AxImageCropDb as AxFieldAxImageCropDb  # pylint: disable=unused-import
import backend.fields.AxNum as AxFieldAxNum  # pylint: disable=unused-import


class InterpreterError(Exception):
    """ Class for AxAction python code errors """


def get_actions(form, current_state=None):
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


def do_exec(action, form):
    """ Executes python commands form AxAction.code

    Args:
        action (AxAction): Current action that is performed
        form (AxForm): Tobe form. Its same as action.form, but it contains
            values from vue form

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
    localz = dict()
    ax = DotMap()  # javascript style dicts item['guid'] == item.guid
    ax.row.guid = form.row_guid
    ax.form = form
    ax.action = action
    ax.schema = ax_schema.schema
    ax.sql = ax_dialects.dialect.custom_query
    ax.paths.uploads = ax_misc.uploads_root_dir
    ax.paths.tmp = ax_misc.tmp_root_dir
    ax.do_action = ax_scheduler.do_action
    for field in form.db_fields:
        ax.row[field.db_name] = field.value
    localz['ax'] = ax
    line_number = None

    try:
        exec(str(action.code), globals(), localz)   # pylint: disable=exec-used
        ret_data = {
            "info": localz['ax_message'] if 'ax_message' in localz else None,
            "error": localz['ax_error'] if 'ax_error' in localz else None,
            "item": localz['ax']['row'],
            "exception": None,
            "abort": localz['ax_abort'] if 'ax_abort' in localz else None
        }
        return ret_data
    except SyntaxError as err:
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
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        del cl, exc
        # line_number = traceback.extract_tb(tb)[-1][1]
        line_number = traceback.extract_tb(tb)[1].lineno
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


def get_before_form(row_guid, form, ax_action):
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
        before_result = ax_dialects.dialect.select_one(
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
                if field.value and field.field_type.value_type == 'JSON':
                    field.value = json.loads(field.value)

    before_form = copy.deepcopy(tobe_form)
    return before_form, tobe_form


def run_field_backend(field, action, before_form, tobe_form, current_user,
                      when='before', query_type='update'):
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
            new_value = method_to_call(
                field=field,
                before_form=before_form,
                tobe_form=tobe_form,
                action=action,
                current_user=current_user)
            return new_value
    return field.value


class DoAction(graphene.Mutation):
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
        action_guid (str): Guid of AxAction that is performed
        values (str): JSON from AxForm.vue with values of form
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
    """
    class Arguments:  # pylint: disable=missing-docstring
        row_guid = graphene.String(required=False, default_value=None)
        form_guid = graphene.String(required=False, default_value=None)
        form_db_name = graphene.String(required=False, default_value=None)
        action_guid = graphene.String(required=False, default_value=None)
        action_db_name = graphene.String(required=False, default_value=None)
        values = graphene.String()
        modal_guid = graphene.String(required=False, default_value=None)

    form = graphene.Field(Form)
    new_guid = graphene.String()
    messages = graphene.String()
    modal_guid = graphene.String()
    ok = graphene.Boolean()

    def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            values_string = args.get('values')
            values = json.loads(values_string)
            row_guid = args.get('row_guid')
            modal_guid = args.get('modal_guid')
            form_guid = args.get('form_guid')
            form_db_name = args.get('form_db_name')
            action_guid = args.get('action_guid')
            action_db_name = args.get('action_db_name')
            new_guid = uuid.uuid4()
            current_user = None  # TODO: implement users

            # 0. Get AxForm
            ax_form = None
            if form_guid:
                ax_form = ax_model.db_session.query(AxForm).filter(
                    AxForm.guid == uuid.UUID(form_guid)
                ).first()
            elif form_db_name:
                ax_form = ax_model.db_session.query(AxForm).filter(
                    AxForm.db_name == form_db_name
                ).first()
            else:
                raise ValueError(
                    'doAction GQL - form guid or db_name required')

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
            before_form, tobe_form = get_before_form(
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
                    field.value = run_field_backend(
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
                code_result = do_exec(action=ax_action, form=tobe_form)
                messages = {
                    "exception": code_result["exception"],
                    "error": code_result["error"],
                    "info": code_result["info"]
                }
                messages_json = json.dumps(messages)
                if code_result['abort'] or code_result["exception"]:
                    return DoAction(
                        form=before_form,
                        new_guid=None,
                        messages=messages_json,
                        modal_guid=modal_guid,
                        ok=False)
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
                ax_dialects.dialect.insert(
                    form=tobe_form,
                    to_state_name=ax_action.to_state.name,
                    new_guid=new_guid
                )
            elif query_type == 'delete':
                ax_dialects.dialect.delete(
                    form=tobe_form,
                    row_guid=tobe_form.row_guid
                )
                return_guid = None
            else:
                ax_dialects.dialect.update(
                    form=tobe_form,
                    to_state_name=ax_action.to_state.name,
                    row_guid=tobe_form.row_guid
                )

            # 7. Run after backend code for each field.
            for field in after_form.no_tab_fields:
                if field.field_type.is_backend_available:
                    field.value = run_field_backend(
                        when='after',
                        query_type=query_type,
                        field=field,
                        action=ax_action,
                        before_form=before_form,
                        tobe_form=after_form,
                        current_user=current_user)

            # 8. Fire all web-socket subscribtions. Notify of action performed
            subscription_form = AxForm()
            subscription_form.guid = tobe_form.guid
            subscription_form.icon = tobe_form.icon
            subscription_form.db_name = tobe_form.db_name
            subscription_form.row_guid = tobe_form.row_guid
            subscription_form.modal_guid = modal_guid

            ax_pubsub.publisher.publish(
                aiopubsub.Key('do_action'), subscription_form)

            ok = True
            return DoAction(
                form=tobe_form,
                new_guid=return_guid,
                messages=messages_json,
                modal_guid=modal_guid,
                ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DoAction.')
            raise


class ActionSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""
    action_notify = graphene.Field(
        Form,
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
                    guid (str): AxForm.guid of current form
                    icon (str): font-awesome icon
                    db_name (str): AxForm.db_name of current form
                    row_guid (str): Guid of row on wich action is performed
                    modal_guid (str): Guid generated by AxForm.vue.
                        It used in web-socket subscribtion. If current form is
                        performing this action - it doesnot need to notify user
                        of performed action
        """
        del info
        try:
            subscriber = aiopubsub.Subscriber(
                ax_pubsub.hub, 'action_notify_subscriber')
            subscriber.subscribe(aiopubsub.Key('do_action'))
            while True:
                key, payload = await subscriber.consume()
                del key
                if payload.db_name == form_db_name:
                    if row_guid is None or row_guid == payload.row_guid:
                        yield payload
        except asyncio.CancelledError:
            await subscriber.remove_all_listeners()


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
        query = Action.get_query(info=info)
        ax_action = query.filter(AxAction.guid == uuid.UUID(guid)).first()
        return ax_action

    async def resolve_actions_avalible(self, info, form_db_name,
                                       current_state=None, update_time=None):
        """ Gets AxActions for current state """
        # TODO: Add permissions based on roles and current user
        try:
            del update_time, info
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == form_db_name
            ).first()
            ax_actions = get_actions(form=ax_form, current_state=current_state)

            return ax_actions
        except Exception:
            logger.exception('Error in gql query - resolve_actions_avalible.')
            raise


class ActionMutations(graphene.ObjectType):
    """Combine all mutations"""
    do_action = DoAction.Field()
