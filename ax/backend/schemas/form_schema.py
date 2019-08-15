"""This is part of GraphQL schema (Mutaions, Queryes, Subscriptions).
Defines manipulation with form AxForm.
All mutations are used in form constructor - create/update/delete for Tab, Field
Query form_data is used in AxForm.vue as main form query.
"""

import uuid
import graphene
from loguru import logger
from backend.model import AxForm, AxField, AxFieldType, \
    AxRoleFieldPermission, AxColumn, AxRole
import backend.model as ax_model
import backend.dialects as ax_dialects
from backend.schemas.types import Form, Field, PositionInput, \
    RoleFieldPermission
import backend.schemas.action_schema as action_schema
import ujson as json


async def set_form_values(ax_form, row_guid):
    """ Select row from DB and set AxForm.fields values, state and rowGuid

    Args:
        ax_form (AxForm): empty AxForm, without field values
        row_guid (str): Guid or AxNum of row

    Returns:
        AxForm: Form with field values
    """
    # TODO get list of fields that user have permission
    allowed_fields = []
    for field in ax_form.db_fields:
        allowed_fields.append(field)

    result = await ax_dialects.dialect.select_one(
        form=ax_form,
        fields_list=allowed_fields,
        row_guid=row_guid)

    if result:
        ax_form.current_state_name = result[0]['axState']
        ax_form.row_guid = result[0]['guid']
        # populate each AxField with data
        for field in ax_form.fields:
            if field in allowed_fields:
                field.value = await ax_dialects.dialect.get_value(
                    type_name=field.field_type.value_type,
                    value=result[0][field.db_name])
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
        guid = graphene.String()    # AxField guid
        name = graphene.String()    # new name

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
    """ Creates AxField

    Arguments:
        form_guid (str): Guid of AxForm
        name (str): Name of new field. Default from en.json
        tag (str): Tag of created field type. Example - AxNum or AxString
        positions (List(PositionInput)): List of positions for all fields
            of form. When field added, we must change position of all fields
            that are lower then inserted.
        position (int): Position of created field
        parent (str): Guid of tab (AxField) wich is parent to current field

    Returns:
        field: Created AxField
        permissions: Default admin permissions that were created. Used to
            update vuex store of workflow constructor.
    """
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
        import backend.schema as ax_schema
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

            # If db table already have {db_name} column -> add digit to db_name
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
                await ax_dialects.dialect.add_column(
                    table=ax_form.db_name,
                    db_name=ax_field.db_name,
                    type_name=ax_field_type.value_type)

            ax_model.db_session.commit()

            # Update positions of all fields that are lower then created field
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
            ax_schema.init_schema()  # re-create GQL schema

            ok = True
            return CreateField(field=ax_field, permissions=permissions, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateTab.')
            raise


class UpdateField(graphene.Mutation):
    """ Updates AxField

    Arguments:
        guid (str): Guid of AxField that needs update
        name (str): New field name
        db_name (str): New db_name of field
        is_required (bool): Is field required
        is_whole_row (bool): Is field always displayed in whole row
        options_json (JSONString): Json wich is transformed to dict by graphene.
            Contains public field options that are passed to vue
        private_options_json (JSONString): Contains options that are visible
            only in python backend actions. Not visible in Vue.

    Returns:
        field (AxField): Created field

    """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        db_name = graphene.String()
        is_required = graphene.Boolean(required=False, default_value=None)
        is_whole_row = graphene.Boolean(required=False, default_value=None)
        options_json = graphene.JSONString(required=False, default_value=None)
        private_options_json = graphene.JSONString(
            required=False, default_value=None)

    ok = graphene.Boolean()
    field = graphene.Field(Field)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        import backend.schema as ax_schema
        del info
        try:
            guid = args.get('guid')
            name = args.get('name')
            db_name = args.get('db_name')
            is_required = args.get('is_required')
            is_whole_row = args.get('is_whole_row')
            options_json = args.get('options_json')
            private_options_json = args.get('private_options_json')

            schema_needs_update = False

            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(guid)
            ).first()

            if name:
                ax_field.name = name

            if db_name and db_name != ax_field.db_name:
                db_name_error = False
                for field in ax_field.form.fields:
                    if field.db_name == db_name and (
                            field.guid != uuid.UUID(guid)):
                        db_name_error = True

                if db_name_error:
                    db_name = db_name + '_enother'

                await ax_dialects.dialect.rename_column(
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

            if private_options_json:
                ax_field.private_options_json = json.dumps(
                    private_options_json)

            if is_required is not None:
                ax_field.is_required = is_required

            if is_whole_row is not None:
                if ax_field.field_type.is_always_whole_row:
                    ax_field.is_whole_row = True
                else:
                    ax_field.is_whole_row = is_whole_row

            ax_model.db_session.commit()

            if schema_needs_update:
                ax_schema.init_schema()  # re-create GQL schema

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
        import backend.schema as ax_schema
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
                await ax_dialects.dialect.drop_column(
                    table=ax_field.form.db_name,
                    column=ax_field.db_name
                )

            ax_model.db_session.delete(ax_field)
            ax_model.db_session.commit()
            ax_schema.init_schema()  # re-create GQL schema

            ok = True
            return DeleteField(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteField.')
            raise


class ChangeFieldsPositions(graphene.Mutation):
    """Change position and parent of multiple fields"""
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        positions = graphene.List(PositionInput)  # positions of all fields

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

    async def resolve_form(self, info, db_name=None, update_time=None):
        """ Get AxForm by db_name

        Args:
            db_name (str, optional): AxForm db_name. Defaults to None.
            update_time (str, optional): Used to disable gql caching.

        Returns:
            AxForm: AxForm
        """
        del update_time
        query = Form.get_query(info=info)
        return query.filter(AxForm.db_name == db_name).first()

    async def resolve_form_data(
            self, info, db_name=None, row_guid=None, update_time=None):
        """ Get AxForm by db_name and row guid

        Args:
            db_name (str, optional): AxForm db_name. Defaults to None.
            row_guid (str, optional): Guid of table row or AxNum value.
            update_time (str, optional): Used to disable gql caching.

        Returns:
            AxForm: Form with field values, avaluble actions, state, row_guid
        """
        del update_time  # used to disable gql caching

        query = Form.get_query(info=info)
        ax_form = query.filter(AxForm.db_name == db_name).first()

        if row_guid is not None:
            ax_form = await set_form_values(ax_form=ax_form, row_guid=row_guid)

        ax_form.avalible_actions = await action_schema.get_actions(
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
