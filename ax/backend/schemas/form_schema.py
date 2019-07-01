"""Defines Form Scheme and all mutations"""

import uuid
import graphene
from loguru import logger

from backend.model import AxForm, AxField, AxFieldType, \
    AxRoleFieldPermission, AxColumn, AxRole

import backend.model as ax_model
import backend.dialects as ax_dialects
import backend.schema as ax_schema

from backend.schemas.types import Form, Field, PositionInput, \
    RoleFieldPermission
import backend.schemas.workflow_schema as workflow_schema
import ujson as json


def set_form_values(ax_form, row_guid):
    """ Sets AxForm fields values + state """
    # TODO get list of fields that user have permission
    allowed_fields = []
    for field in ax_form.db_fields:
        allowed_fields.append(field)

    result = ax_dialects.dialect.select_one(
        form_db_name=ax_form.db_name,
        fields_list=allowed_fields,
        row_guid=row_guid)

    if result:
        ax_form.current_state_name = result[0]['axState']
        # populate each AxField with data
        for field in ax_form.fields:
            if field in allowed_fields:
                field.value = result[0][field.db_name]
            if field.is_tab is False and field.is_virtual:
                field.value = result[0][field.field_type.default_db_name]

    return ax_form


class CreateTab(graphene.Mutation):
    """ Creates AxField wich is tab """
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        name = graphene.String()

    ok = graphene.Boolean()
    field = graphene.Field(Field)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            form_guid = args.get('form_guid')
            name = args.get('name')

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(form_guid)
            ).first()

            ax_field = AxField()
            ax_field.name = name
            ax_field.form_guid = ax_form.guid
            ax_field.is_tab = True
            ax_field.position = len(
                [i for i in ax_form.fields if i.is_tab is True]) + 1
            ax_model.db_session.add(ax_field)
            ax_model.db_session.commit()

            ok = True
            return CreateTab(field=ax_field, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateTab.')
            raise


class UpdateTab(graphene.Mutation):
    """ Updates AxField witch is tab """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()

    ok = graphene.Boolean()
    field = graphene.Field(Field)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            name = args.get('name')

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(guid)
            ).first()
            ax_field.name = name
            ax_model.db_session.commit()

            ok = True
            return UpdateTab(field=ax_field, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateTab.')
            raise


class DeleteTab(graphene.Mutation):
    """ Deletes AxField witch is tab """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(guid)
            ).first()
            ax_model.db_session.delete(ax_field)
            ax_model.db_session.commit()

            ok = True
            return DeleteTab(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteTab.')
            raise


class CreateField(graphene.Mutation):
    """ Creates AxField """
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        name = graphene.String()
        tag = graphene.String()
        positions = graphene.List(PositionInput)
        position = graphene.Int()
        parent = graphene.String()

    ok = graphene.Boolean()
    field = graphene.Field(Field)
    permissions = graphene.List(RoleFieldPermission)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        del info
        try:
            form_guid = args.get('form_guid')
            name = args.get('name')
            tag = args.get('tag')
            position = args.get('position')
            positions = args.get('positions')
            parent = args.get('parent')

            cur_name = None
            cur_db_name = None
            name_is_checked = False
            cur_num = 1

            ax_field_type = ax_model.db_session.query(AxFieldType).filter(
                AxFieldType.tag == tag
            ).first()

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(form_guid)
            ).first()

            while name_is_checked is False:
                error_flag = False
                if cur_num > 1:
                    cur_name = name + " " + str(cur_num)
                else:
                    cur_name = name
                cur_db_name = ax_field_type.default_db_name + str(cur_num)
                for field in ax_form.fields:
                    if field.name == cur_name or field.db_name == cur_db_name:
                        error_flag = True
                if error_flag is True:
                    cur_num = cur_num + 1
                else:
                    name_is_checked = True
                    break

            ax_field = AxField()
            ax_field.name = cur_name
            ax_field.db_name = cur_db_name
            ax_field.form_guid = ax_form.guid
            ax_field.value_type = ax_field_type.value_type
            ax_field.field_type_tag = ax_field_type.tag
            ax_field.options_json = "{}"
            ax_field.position = position
            ax_field.parent = uuid.UUID(parent) if parent is not None else None

            if ax_field_type.is_always_whole_row:
                ax_field.is_whole_row = True

            ax_model.db_session.add(ax_field)

            if ax_field_type.is_virtual is False:
                ax_dialects.dialect.add_column(
                    table=ax_form.db_name,
                    db_name=ax_field.db_name,
                    type_name=ax_field_type.value_type)

            ax_model.db_session.commit()

            for field in ax_form.fields:
                for pos in positions:
                    if field.guid == uuid.UUID(pos.guid):
                        current_parent = None
                        if pos.parent != '#':
                            current_parent = uuid.UUID(pos.parent)
                        field.position = pos.position
                        field.parent = current_parent

            # add permission for default admin role on every state
            admin_role = ax_model.db_session.query(AxRole).filter(
                AxRole.is_admin.is_(True)
            ).filter(AxRole.form_guid == ax_form.guid).first()

            permissions = []
            for state in ax_form.states:
                perm = AxRoleFieldPermission()
                perm.form_guid = ax_form.guid
                perm.state_guid = state.guid
                perm.role_guid = admin_role.guid
                perm.field_guid = ax_field.guid
                perm.read = True
                perm.edit = True
                ax_model.db_session.add(perm)
                permissions.append(perm)

            ax_model.db_session.commit()
            ax_schema.init_schema()

            ok = True
            return CreateField(field=ax_field, permissions=permissions, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateTab.')
            raise


class UpdateField(graphene.Mutation):
    """ Updates AxField """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        db_name = graphene.String()
        is_required = graphene.Boolean()
        is_whole_row = graphene.Boolean()
        options_json = graphene.JSONString()

    ok = graphene.Boolean()
    field = graphene.Field(Field)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        del info
        try:
            guid = args.get('guid')
            name = args.get('name')
            db_name = args.get('db_name')
            is_required = args.get('is_required')
            is_whole_row = args.get('is_whole_row')
            options_json = args.get('options_json')

            schema_needs_update = False

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(guid)
            ).first()

            if name:
                ax_field.name = name

            if db_name:
                db_name_error = False
                for field in ax_field.form.fields:
                    if field.db_name == db_name and field.guid != uuid.UUID(guid):
                        db_name_error = True

                if db_name_error:
                    db_name = db_name + '_enother'

                ax_dialects.dialect.rename_column(
                    table=ax_field.form.db_name,
                    old_name=ax_field.db_name,
                    new_name=db_name,
                    type_name=ax_field.field_type.value_type
                )

                ax_field.db_name = db_name
                ax_model.db_session.commit()
                schema_needs_update = True

            if options_json:
                ax_field.options_json = json.dumps(options_json)

            if is_required is not None:
                ax_field.is_required = is_required

            if is_whole_row is not None:
                if ax_field.field_type.is_always_whole_row:
                    ax_field.is_whole_row = True
                else:
                    ax_field.is_whole_row = is_whole_row

            ax_model.db_session.commit()

            if schema_needs_update:
                ax_schema.init_schema()

            ok = True
            return CreateTab(field=ax_field, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateField.')
            raise


class DeleteField(graphene.Mutation):
    """ Deletes AxField """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(guid)
            ).first()

            ax_model.db_session.query(AxRoleFieldPermission).filter(
                AxRoleFieldPermission.field_guid == ax_field.guid).delete()
            ax_model.db_session.query(AxColumn).filter(
                AxColumn.field_guid == ax_field.guid).delete()

            if ax_field.is_tab is False and ax_field.is_virtual is False:
                ax_dialects.dialect.drop_column(
                    table=ax_field.form.db_name,
                    column=ax_field.db_name
                )

            ax_model.db_session.delete(ax_field)
            ax_model.db_session.commit()
            ax_schema.init_schema()

            ok = True
            return DeleteField(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteField.')
            raise


class ChangeFieldsPositions(graphene.Mutation):
    """Change position and parent of fields"""
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        positions = graphene.List(PositionInput)

    ok = graphene.Boolean()
    fields = graphene.List(Field)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            form_guid = args.get('form_guid')
            positions = args.get('positions')

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(form_guid)
            ).one()

            for field in ax_form.fields:
                for position in positions:
                    if field.guid == uuid.UUID(position.guid):
                        current_parent = None
                        if position.parent != '#':
                            current_parent = uuid.UUID(position.parent)
                        field.parent = current_parent
                        field.position = position.position

            ax_model.db_session.commit()
            query = Field.get_query(info)
            field_list = query.filter(
                AxField.form_guid == uuid.UUID(form_guid)
            ).all()

            ok = True
            return ChangeFieldsPositions(fields=field_list, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - ChangeFieldsPositions.')
            raise


class FormQuery(graphene.ObjectType):
    """Query all data of AxForm and related classes"""
    # all_fields = graphene.List(Field, form_field=graphene.String())
    form = graphene.Field(
        Form,
        db_name=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    form_data = graphene.Field(
        Form,
        db_name=graphene.Argument(type=graphene.String, required=True),
        row_guid=graphene.Argument(type=graphene.String, required=False),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )

    # async def resolve_all_fields(self, info, form_field):
    #     """Get all fields of form"""
    #     del info
    #     try:
    #         field_list = ax_model.db_session.query(AxField).filter(
    #             AxField.form_guid == uuid.UUID(form_field)
    #         ).all()
    #         return field_list
    #     except Exception:
    #         logger.exception('Error in GQL query - resolve_fields.')
    #         raise

    async def resolve_form(self, info, db_name=None, update_time=None):
        """Get AxForm by db_name"""
        del update_time
        query = Form.get_query(info=info)
        return query.filter(AxForm.db_name == db_name).first()

    async def resolve_form_data(self, info, db_name=None, row_guid=None, update_time=None):
        """Get AxForm by db_name and row guid"""
        del update_time

        query = Form.get_query(info=info)
        ax_form = query.filter(AxForm.db_name == db_name).first()

        if row_guid is not None:
            ax_form = set_form_values(ax_form=ax_form, row_guid=row_guid)

        ax_form.avalible_actions = workflow_schema.get_actions(
            form=ax_form,
            current_state=ax_form.current_state_name
        )

        ax_model.db_session.flush()
        return ax_form


class FormMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_tab = CreateTab.Field()
    update_tab = UpdateTab.Field()
    delete_tab = DeleteTab.Field()
    create_field = CreateField.Field()
    update_field = UpdateField.Field()
    delete_field = DeleteField.Field()
    change_fields_positions = ChangeFieldsPositions.Field()
