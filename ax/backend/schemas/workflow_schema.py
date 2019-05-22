""" GQL Chema for Workflow manipulation """
import uuid
import graphene
from loguru import logger
import ujson as json

from backend.model import GUID, AxForm, AxField, AxGrid, AxAction, AxState, \
    AxRole, AxRole2Users, AxRoleFieldPermission, AxState2Role, AxAction2Role, \
    AxColumn, Ax1tomReference
import backend.model as ax_model
import backend.schema as ax_schema

# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import Grid, Column, State, Action, PositionInput, \
    State2Role, Action2Role, RoleFieldPermission, Role
# import ujson as json


class CreateState(graphene.Mutation):
    """Create AxState"""
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        update = graphene.String(required=False, default_value=None)
        form_guid = graphene.String()
        x = graphene.Float()
        y = graphene.Float()

    ok = graphene.Boolean()
    state = graphene.Field(State)
    action = graphene.Field(Action)

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

            update_action = None
            if args.get('update'):
                update_action = AxAction()
                update_action.name = args.get('update')
                update_action.form_guid = args.get('form_guid')
                update_action.from_state_guid = new_state.guid
                update_action.to_state_guid = new_state.guid

                ax_model.db_session.add(update_action)
                ax_model.db_session.commit()

            # TODO: Add default admin role!

            ok = True
            return CreateState(state=new_state, action=update_action, ok=ok)
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

            # TODO: Add default admin roles

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
            if args.get('close_modal'):
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
            state2role = AxState2Role()
            state2role.state_guid = args.get('state_guid')
            state2role.role_guid = args.get('role_guid')

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
                    AxState2Role.role_guid == uuid.UUID(role_guid) and
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
            action2role = AxAction2Role()
            action2role.action_guid = args.get('action_guid')
            action2role.role_guid = args.get('role_guid')

            ax_model.db_session.add(action2role)
            ax_model.db_session.commit()

            ok = True
            return AddRoleToState(action2role=action2role, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - AddRoleToAction.')
            raise


class DeleteRoleFromAction(graphene.Mutation):
    """Deletes AxAction2Role"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()
    role_guid = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            role2action = ax_model.db_session.query(AxAction2Role).filter(
                AxAction2Role.guid == uuid.UUID(guid)
            ).first()
            role_guid = role2action.role_guid
            ax_model.db_session.delete(role2action)
            ax_model.db_session.commit()

            ok = True
            return DeleteRoleFromState(deleted=guid, ok=ok, role_guid=role_guid)
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
            return_permissions = []
            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.id == uuid.UUID(field_guid)).first()

            if not ax_field.is_tab:
                current_fields_guids.append(ax_field.guid)
            else:
                for field in ax_field.ax_object.fields:
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
                    ax_perm.field_guid = uuid.UUID(field_guid)
                    ax_model.db_session.add(ax_perm)

                ax_perm.read = read
                ax_perm.edit = edit

                ax_model.db_session.commit()
                return_permissions.append(ax_perm)

            ok = True
            return SetStatePermission(permissions=return_permissions, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - SetStatePermission.')
            raise


class WorkflowQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
    pass


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
