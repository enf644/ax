"""Defines Form Scheme and all mutations"""

import uuid
import graphene
from loguru import logger

from backend.model import AxForm, AxField, AxFieldType
import backend.model as ax_model
# import backend.cache as ax_cache # TODO use cache!
import backend.dialects as ax_dialects
from backend.schemas.types import Form, Field, PositionInput


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
            ax_model.db_session.add(ax_field)

            if ax_field.value_type != "VIRTUAL":
                sql = ax_dialects.dialect.add_column(
                    table=ax_form.db_name,
                    db_name=ax_field.db_name,
                    type_name=ax_field_type.value_type)
                ax_model.db_session.execute(sql)

            ax_model.db_session.commit()

            for field in ax_form.fields:
                for pos in positions:
                    if field.guid == uuid.UUID(pos.guid):
                        current_parent = None
                        if pos.parent != '#':
                            current_parent = uuid.UUID(pos.parent)
                        field.position = pos.position
                        field.parent = current_parent

            ax_model.db_session.commit()

            ok = True
            return CreateTab(field=ax_field, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateTab.')
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
    all_fields = graphene.List(Field, form_field=graphene.String())
    form = graphene.Field(
        Form,
        db_name=graphene.Argument(type=graphene.String, required=True)
    )

    async def resolve_all_fields(self, info, form_field):
        """Get all fields of form"""
        del info
        try:
            field_list = ax_model.db_session.query(AxField).filter(
                AxField.form_guid == uuid.UUID(form_field)
            ).all()
            return field_list
        except Exception:
            logger.exception('Error in GQL query - resolve_fields.')
            raise

    async def resolve_form(self, info, db_name):
        """Get AxForm by db_name"""
        query = Form.get_query(info=info)
        return query.filter(AxForm.db_name == db_name).first()


class FormMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_tab = CreateTab.Field()
    create_field = CreateField.Field()
    change_fields_positions = ChangeFieldsPositions.Field()
