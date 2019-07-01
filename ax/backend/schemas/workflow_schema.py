""" GQL Chema for Workflow manipulation """
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

from backend.model import AxForm, AxField, AxAction, AxState, \
    AxRole, AxRoleFieldPermission, AxState2Role, AxAction2Role
import backend.model as ax_model
import backend.dialects as ax_dialects
import backend.pubsub as ax_pubsub
import backend.misc as ax_misc

# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import  State, Action, \
    State2Role, Action2Role, RoleFieldPermission, Role, Form

import backend.fields.Ax1tom as AxFieldAx1tom
import backend.fields.Ax1tomTable as AxFieldAx1tomTable
import backend.fields.AxChangelog as AxFieldAxChangelog
import backend.fields.AxFiles as AxFieldAxFiles
import backend.fields.AxImageCropDb as AxFieldAxImageCropDb


def get_actions(form, current_state=None):
    """ get actions for current state """
    # TODO: filter actions, filter fields based on state and user
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



class CreateState(graphene.Mutation):
    """Create AxState"""
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        # update argument is default self-action name.
        # As it is different for locales it
        # is passed from UI
        update = graphene.String(required=False, default_value=None)
        form_guid = graphene.String()
        x = graphene.Float()
        y = graphene.Float()

    ok = graphene.Boolean()
    state = graphene.Field(State)
    action = graphene.Field(Action)
    permissions = graphene.List(RoleFieldPermission)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            new_state = AxState()
            new_state.name = args.get('name')
            new_state.form_guid = args.get('form_guid')
            new_state.x = args.get('x')
            new_state.y = args.get('y')

            ax_model.db_session.add(new_state)
            ax_model.db_session.commit()

            # Create default self-action
            update_action = None
            if args.get('update'):
                update_action = AxAction()
                update_action.name = args.get('update')
                update_action.form_guid = uuid.UUID(args.get('form_guid'))
                update_action.from_state_guid = new_state.guid
                update_action.to_state_guid = new_state.guid

                ax_model.db_session.add(update_action)
                ax_model.db_session.commit()

            # Add default admin role
            admin_role = ax_model.db_session.query(AxRole).filter(
                AxRole.form_guid == uuid.UUID(args.get('form_guid'))
            ).filter(
                AxRole.is_admin.is_(True)
            ).first()

            # Add permissions for default admin role
            permissions = []
            if admin_role:
                state2role = AxState2Role()
                state2role.state_guid = new_state.guid
                state2role.role_guid = admin_role.guid
                ax_model.db_session.add(state2role)
                ax_model.db_session.commit()

                ax_form = ax_model.db_session.query(AxForm).filter(
                    AxForm.guid == uuid.UUID(args.get('form_guid'))
                ).first()

                for field in ax_form.fields:
                    perm = AxRoleFieldPermission()
                    perm.form_guid = ax_form.guid
                    perm.state_guid = new_state.guid
                    perm.role_guid = admin_role.guid
                    perm.field_guid = field.guid
                    perm.read = True
                    perm.edit = True
                    ax_model.db_session.add(perm)
                    permissions.append(perm)

                ax_model.db_session.commit()

            ok = True
            return CreateState(
                state=new_state,
                action=update_action,
                permissions=permissions,
                ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateState.')
            raise


class UpdateState(graphene.Mutation):
    """Update AxState"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        x = graphene.Float()
        y = graphene.Float()

    ok = graphene.Boolean()
    state = graphene.Field(State)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            ax_state = ax_model.db_session.query(AxState).filter(
                AxState.guid == uuid.UUID(args.get('guid'))
            ).first()
            if args.get('name'):
                ax_state.name = args.get('name')
            if args.get('x'):
                ax_state.x = args.get('x')
            if args.get('y'):
                ax_state.y = args.get('y')

            ax_model.db_session.commit()

            ok = True
            return UpdateState(state=ax_state, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateState.')
            raise


class DeleteState(graphene.Mutation):
    """Deletes AxState"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            ax_state = ax_model.db_session.query(AxState).filter(
                AxState.guid == uuid.UUID(guid)
            ).first()

            ax_model.db_session.query(AxAction).filter(
                AxAction.from_state_guid == uuid.UUID(guid)
            ).delete()

            ax_model.db_session.query(AxAction).filter(
                AxAction.to_state_guid == uuid.UUID(guid)
            ).delete()

            ax_model.db_session.delete(ax_state)
            ax_model.db_session.commit()

            ok = True
            return DeleteState(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteState.')
            raise


class CreateAction(graphene.Mutation):
    """Creates AxAction"""
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        name = graphene.String()
        from_state_guid = graphene.String()
        to_state_guid = graphene.String()

    ok = graphene.Boolean()
    action = graphene.Field(Action)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            new_action = AxAction()
            new_action.name = args.get('name')
            new_action.form_guid = args.get('form_guid')
            new_action.from_state_guid = args.get('from_state_guid')
            new_action.to_state_guid = args.get('to_state_guid')

            ax_model.db_session.add(new_action)
            ax_model.db_session.commit()

            # Add default admin role
            admin_role = ax_model.db_session.query(AxRole).filter(
                AxRole.form_guid == uuid.UUID(args.get('form_guid'))
            ).filter(
                AxRole.is_admin.is_(True)
            ).first()

            if admin_role:
                action2role = AxAction2Role()
                action2role.action_guid = new_action.guid
                action2role.role_guid = admin_role.guid
                ax_model.db_session.add(action2role)
                ax_model.db_session.commit()

            ok = True
            return CreateAction(action=new_action, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateAction.')
            raise


class UpdateAction(graphene.Mutation):
    """Updates AxAction"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String(required=False, default_value=None)
        code = graphene.String(required=False, default_value=None)
        confirm_text = graphene.String(required=False, default_value=None)
        close_modal = graphene.Boolean(required=False, default_value=None)
        icon = graphene.String(required=False, default_value=None)
        radius = graphene.Float(required=False, default_value=None)

    ok = graphene.Boolean()
    action = graphene.Field(Action)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            ax_action = ax_model.db_session.query(AxAction).filter(
                AxAction.guid == uuid.UUID(args.get('guid'))
            ).first()

            if args.get('name'):
                ax_action.name = args.get('name')
            if args.get('code'):
                ax_action.code = args.get('code')
            if args.get('confirm_text'):
                ax_action.confirm_text = args.get('confirm_text')

            ax_action.close_modal = args.get('close_modal')
            if args.get('icon'):
                ax_action.icon = args.get('icon')
            if args.get('radius') is not None:
                ax_action.radius = args.get('radius')

            ax_model.db_session.commit()

            ok = True
            return UpdateAction(action=ax_action, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateAction.')
            raise


class DeleteAction(graphene.Mutation):
    """Deletes AxAction"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            ax_action = ax_model.db_session.query(AxAction).filter(
                AxAction.guid == uuid.UUID(guid)
            ).first()

            ax_model.db_session.delete(ax_action)
            ax_model.db_session.commit()

            ok = True
            return DeleteAction(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteAction.')
            raise


class CreateRole(graphene.Mutation):
    """Creates AxRole"""
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        name = graphene.String()

    ok = graphene.Boolean()
    role = graphene.Field(Role)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info

            ax_role = AxRole()
            ax_role.name = args.get('name')
            ax_role.form_guid = args.get('form_guid')

            ax_model.db_session.add(ax_role)
            ax_model.db_session.commit()
            ok = True

            return CreateRole(role=ax_role, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateRole.')
            raise


class UpdateRole(graphene.Mutation):
    """Updates AxRole"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String(required=False, default_value=None)
        icon = graphene.String(required=False, default_value=None)

    ok = graphene.Boolean()
    role = graphene.Field(Role)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            ax_role = ax_model.db_session.query(AxRole).filter(
                AxRole.guid == uuid.UUID(args.get('guid'))
            ).first()

            if args.get('name'):
                ax_role.name = args.get('name')

            if args.get('icon'):
                ax_role.icon = args.get('icon')

            ok = True
            return UpdateRole(role=ax_role, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateRole.')
            raise


class DeleteRole(graphene.Mutation):
    """Deletes AxRole"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            ax_role = ax_model.db_session.query(AxRole).filter(
                AxRole.guid == uuid.UUID(guid)
            ).first()

            ax_model.db_session.delete(ax_role)
            ax_model.db_session.commit()

            ok = True
            return DeleteRole(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteRole.')
            raise


class AddRoleToState(graphene.Mutation):
    """Create AxState2Role"""
    class Arguments:  # pylint: disable=missing-docstring
        state_guid = graphene.String()
        role_guid = graphene.String()

    ok = graphene.Boolean()
    state2role = graphene.Field(State2Role)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            role_guid = args.get('role_guid')
            state_guid = args.get('state_guid')
            existing_state2role = ax_model.db_session.query(
                AxState2Role
            ).filter(
                AxState2Role.role_guid == uuid.UUID(role_guid)
            ).filter(
                AxState2Role.state_guid == uuid.UUID(state_guid)
            ).first()

            if existing_state2role:
                ok = True
                return AddRoleToState(state2role=existing_state2role, ok=ok)

            state2role = AxState2Role()
            state2role.state_guid = uuid.UUID(state_guid)
            state2role.role_guid = uuid.UUID(role_guid)

            ax_model.db_session.add(state2role)
            ax_model.db_session.commit()

            ok = True
            return AddRoleToState(state2role=state2role, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - AddRoleToState.')
            raise


class DeleteRoleFromState(graphene.Mutation):
    """Deletes AxState2Role"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        role_guid = graphene.String()
        state_guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()
    role_guid = graphene.String()
    state_guid = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            role_guid = args.get('role_guid')
            state_guid = args.get('state_guid')

            role2state = None
            if guid:
                role2state = ax_model.db_session.query(AxState2Role).filter(
                    AxState2Role.guid == uuid.UUID(guid)
                ).first()
            else:
                role2state = ax_model.db_session.query(AxState2Role).filter(
                    AxState2Role.role_guid == uuid.UUID(role_guid)
                ).filter(
                    AxState2Role.state_guid == uuid.UUID(state_guid)
                ).first()

            the_role_guid = role2state.role_guid
            the_state_guid = role2state.state_guid

            ax_model.db_session.delete(role2state)
            ax_model.db_session.commit()

            ok = True
            return DeleteRoleFromState(
                deleted=guid,
                role_guid=the_role_guid,
                state_guid=the_state_guid,
                ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteRoleFromState.')
            raise


class AddRoleToAction(graphene.Mutation):
    """Create AxAction2Role"""
    class Arguments:  # pylint: disable=missing-docstring
        action_guid = graphene.String()
        role_guid = graphene.String()

    ok = graphene.Boolean()
    action2role = graphene.Field(Action2Role)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info

            role_guid = args.get('role_guid')
            action_guid = args.get('action_guid')
            existing_action2role = ax_model.db_session.query(
                AxAction2Role
            ).filter(
                AxAction2Role.role_guid == uuid.UUID(role_guid)
            ).filter(
                AxAction2Role.action_guid == uuid.UUID(action_guid)
            ).first()

            if existing_action2role:
                ok = True
                return AddRoleToAction(action2role=existing_action2role, ok=ok)

            action2role = AxAction2Role()
            action2role.action_guid = uuid.UUID(action_guid)
            action2role.role_guid = uuid.UUID(role_guid)

            ax_model.db_session.add(action2role)
            ax_model.db_session.commit()

            ok = True
            return AddRoleToAction(action2role=action2role, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - AddRoleToAction.')
            raise


class DeleteRoleFromAction(graphene.Mutation):
    """Deletes AxAction2Role"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        action_guid = graphene.String()
        role_guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()
    role_guid = graphene.String()
    action_guid = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            action_guid = args.get('action_guid')
            role_guid = args.get('role_guid')

            role2action = None
            if guid:
                role2action = ax_model.db_session.query(AxAction2Role).filter(
                    AxAction2Role.guid == uuid.UUID(guid)
                ).first()
            else:
                role2action = ax_model.db_session.query(AxAction2Role).filter(
                    AxAction2Role.role_guid == uuid.UUID(role_guid)
                ).filter(
                    AxAction2Role.action_guid == uuid.UUID(action_guid)
                ).first()

            deleted = role2action.guid
            ax_model.db_session.delete(role2action)
            ax_model.db_session.commit()

            ok = True
            return DeleteRoleFromAction(
                deleted=deleted,
                ok=ok,
                role_guid=role_guid,
                action_guid=action_guid)
        except Exception:
            logger.exception('Error in gql mutation - DeleteRoleFromState.')
            raise


class SetStatePermission(graphene.Mutation):
    """Creates AxRoleFieldPermission or multiple if tab field is presented"""
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        state_guid = graphene.String()
        role_guid = graphene.String()
        field_guid = graphene.String()
        read = graphene.Boolean()
        edit = graphene.Boolean()

    ok = graphene.Boolean()
    permissions = graphene.List(RoleFieldPermission)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info

            form_guid = args.get('form_guid')
            state_guid = args.get('state_guid')
            role_guid = args.get('role_guid')
            field_guid = args.get('field_guid')
            read = args.get('read')
            edit = args.get('edit')

            current_fields_guids = []

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(field_guid)).first()

            if not ax_field.is_tab:
                current_fields_guids.append(ax_field.guid)
            else:
                for field in ax_field.form.fields:
                    if field.parent == ax_field.guid:
                        current_fields_guids.append(field.guid)

            for current_guid in current_fields_guids:
                ax_perm = ax_model.db_session.query(
                    AxRoleFieldPermission
                ).filter(
                    AxRoleFieldPermission.state_guid == uuid.UUID(state_guid)
                ).filter(
                    AxRoleFieldPermission.role_guid == uuid.UUID(role_guid)
                ).filter(
                    AxRoleFieldPermission.field_guid == current_guid
                ).first()

                if ax_perm is None:
                    ax_perm = AxRoleFieldPermission()
                    ax_perm.form_guid = uuid.UUID(form_guid)
                    ax_perm.role_guid = uuid.UUID(role_guid)
                    ax_perm.field_guid = current_guid
                    ax_perm.state_guid = uuid.UUID(state_guid)
                    ax_perm.read = read
                    ax_perm.edit = edit
                    ax_model.db_session.add(ax_perm)
                    ax_model.db_session.commit()
                else:
                    ax_perm.read = read
                    ax_perm.edit = edit
                    ax_model.db_session.commit()

            return_permissions = ax_model.db_session.query(
                AxRoleFieldPermission
            ).filter(
                AxRoleFieldPermission.state_guid == uuid.UUID(state_guid)
            ).all()

            ok = True
            return SetStatePermission(permissions=return_permissions, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - SetStatePermission.')
            raise



class InterpreterError(Exception):
    """ Class for AxAction python code errors """


def do_exec(action, form):
    """ executes python commands form AxAction.code """
    localz = dict()
    localz['ax_obj'] = form
    item = DotMap()
    item['guid'] = form.row_guid
    item['ax_from_state'] = action.from_state.name
    item['ax_to_state'] = action.to_state.name
    for field in form.db_fields:
        item[field.db_name] = field.value
    localz['item'] = item

    try:
        exec(str(action.code), globals(), localz)
        ret_data = {
            "info": localz['ax_message'] if 'ax_message' in localz else None,
            "error": localz['ax_error'] if 'ax_error' in localz else None,
            "item": localz['item'],
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
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        del cl, exc
        line_number = traceback.extract_tb(tb)[-1][1]
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


def get_before_form(row_guid, form_guid, ax_action):
    """Constructs before_form AxForm object and populate fields with
    values of specific row. AxForm.fields[0].value

    Args:
        row_guid (str): guid of specific row
        form_guid (str): guid of AxForm
        ax_action (AxAction): AxAction wich is currently happening

    Returns:
       before_object (AxForm), tobe_object(AxForm): before_object is AxForm
       with field values of specific row. tobe_row is dummy for future
       population"""
    tobe_form = ax_model.db_session.query(AxForm).filter(
        AxForm.guid == uuid.UUID(form_guid)
    ).first()

    if row_guid:
        fields_names = [field for field in tobe_form.db_fields]
        before_result = ax_dialects.dialect.select_one(
            form_db_name=tobe_form.db_name,
            fields_list=fields_names,
            row_guid=row_guid)

        if not before_result:
            raise Exception(
                'Error in DoAction. Cant find row for action')

        tobe_form.current_state_name = before_result[0]['axState']
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


def run_field_backend(field, action, before_form, tobe_form, current_user,\
    when='before', query_type='update'):
    """Some field types need backend execution on insert/update/delete

    Args:
        field (AxField): contains current .value of updated field
        action (AxAction): Just for info
        before_form (AxForm): Just for info
        tobe_form (AxForm): Just for info
        current_user (AxUser): Just for info
        when (str, optional): Can be 'before' or 'after'. Defaults to 'before'.
        query_type (str, optional): Can be 'insert', 'update', 'delete'.
        Defaults to 'update'.

    Returns:
        [type]: Returns new field value
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
    """ Performs Action or row """
    class Arguments:  # pylint: disable=missing-docstring
        row_guid = graphene.String(required=False, default_value=None)
        form_guid = graphene.String()
        action_guid = graphene.String()
        values = graphene.String()
        modal_guid = graphene.String(required=False, default_value=None)

    form = graphene.Field(Form)
    new_guid = graphene.String()
    messages = graphene.String()
    modal_guid = graphene.String()
    ok = graphene.Boolean()


    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            values_string = args.get('values')
            values = json.loads(values_string)
            row_guid = args.get('row_guid')
            modal_guid = args.get('modal_guid')
            form_guid = args.get('form_guid')
            new_guid = uuid.uuid4()
            current_user = None #TODO: implement users
            actual_guid = new_guid
            if row_guid:
                actual_guid = row_guid


            # 1. Get AxAction and query_type
            ax_action = ax_model.db_session.query(AxAction).filter(
                AxAction.guid == uuid.UUID(args.get('action_guid'))
            ).first()

            query_type = 'update'
            if ax_action.from_state.is_start:
                query_type = 'insert'
            elif ax_action.to_state.is_deleted:
                query_type = 'delete'


            # 2. Get before_form
            before_form, tobe_form = get_before_form(
                row_guid=row_guid,
                form_guid=form_guid,
                ax_action=ax_action)

            # 3. Assemble tobe_object
            tobe_form.row_guid = actual_guid
            for field in tobe_form.db_fields:
                if field.db_name in values.keys():
                    field.value = values[field.db_name]
                    field.needs_sql_update = True
                if field.field_type.is_updated_always:
                    field.needs_sql_update = True

            # 4. Run before backend code for each field.
            for field in tobe_form.db_fields:
                if field.field_type.is_backend_available:
                    field.value = run_field_backend(
                        when='before',
                        query_type=query_type,
                        field=field,
                        action=ax_action,
                        before_form=before_form,
                        tobe_form=tobe_form,
                        current_user=current_user)


            # 5. Run python action, rewrite tobe_object (not implemented)
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
                    row_guid=row_guid
                )
            else:
                ax_dialects.dialect.update(
                    form=tobe_form,
                    to_state_name=ax_action.to_state.name,
                    row_guid=row_guid
                )

            # 7. Run after backend code for each field.
            for field in after_form.db_fields:
                if field.field_type.is_backend_available:
                    field.value = run_field_backend(
                        when='after',
                        query_type=query_type,
                        field=field,
                        action=ax_action,
                        before_form=before_form,
                        tobe_form=after_form,
                        current_user=current_user)

            # 8. Fire all subscribtions
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
                new_guid=tobe_form.row_guid,
                messages=messages_json,
                modal_guid=modal_guid,
                ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DoAction.')
            raise



class WorkflowSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""
    action_notify = graphene.Field(
        Form,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        row_guid=graphene.Argument(type=graphene.String, required=False))


    async def resolve_action_notify(self, info, form_db_name, row_guid=None):
        """Subscribe to adding new user"""
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




class WorkflowQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
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
        """ get AxAction code and other big settings """
        del update_time
        query = Action.get_query(info=info)
        ax_action = query.filter(AxAction.guid == uuid.UUID(guid)).first()
        return ax_action

    async def resolve_actions_avalible(self, info, form_db_name,
                                       current_state=None, update_time=None):
        """ get AxActions for current state """
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


class WorkflowMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_state = CreateState.Field()
    update_state = UpdateState.Field()
    delete_state = DeleteState.Field()
    create_action = CreateAction.Field()
    update_action = UpdateAction.Field()
    delete_action = DeleteAction.Field()
    create_role = CreateRole.Field()
    update_role = UpdateRole.Field()
    delete_role = DeleteRole.Field()
    add_role_to_state = AddRoleToState.Field()
    delete_role_from_state = DeleteRoleFromState.Field()
    add_role_to_action = AddRoleToAction.Field()
    delete_role_from_action = DeleteRoleFromAction.Field()
    set_state_permission = SetStatePermission.Field()
    do_action = DoAction.Field()
