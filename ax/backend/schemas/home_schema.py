"""Describes schemas for AxForm manipulation in admin home"""
import uuid
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from sqlalchemy import MetaData
from loguru import logger

from backend.misc import convert_column_to_string  # TODO check if needed
from backend.model import GUID, AxForm, AxField  # TODO: check if needed
import backend.model as ax_model
import backend.cache as ax_cache
import backend.dialects as ax_dialects
from backend.schemas.types import Form, Field, PositionInput

convert_sqlalchemy_type.register(GUID)(convert_column_to_string)


def is_db_name_avalible(_db_name) -> bool:
    """Check if table is already exists in database"""
    try:
        meta = MetaData()
        meta.reflect(bind=ax_model.engine)
        db_names = list(meta.tables.keys())
        return _db_name not in db_names
    except Exception:
        logger.exception('Error checking if db_name exists in database.')
        raise


def create_db_table(_db_name: str) -> None:
    """Create database table"""
    try:
        query = ax_dialects.dialect.create_data_table(db_name=_db_name)
    except Exception:
        logger.exception('Error creating new Form. Cant create db table')
        raise


def create_ax_form(_name: str, _db_name: str) -> object:
    """Creates AxForm object"""
    try:
        ax_form = AxForm()
        ax_form.name = _name
        ax_form.db_name = _db_name
        ax_form.tom_label = "{{ax_form_name}} - {{ax_num}}"
        ax_form.icon = "dice-d6"
        ax_model.db_session.add(ax_form)
        ax_model.db_session.commit()
        return ax_form
    except Exception:
        logger.exception('Error creating AxForm object')
        raise


def create_default_tab(ax_form, tab_name) -> None:
    """ Create default AxForm tab """
    try:
        ax_field = AxField()
        ax_field.name = tab_name
        ax_field.form_guid = ax_form.guid
        ax_field.is_tab = True
        ax_field.position = 1
        ax_model.db_session.add(ax_field)
        ax_model.db_session.commit()
    except Exception:
        logger.exception('Error creating default tab.')
        raise


class CreateForm(graphene.Mutation):
    """ Creates AxForm """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        db_name = graphene.String()
        tab_name = graphene.String()

    ok = graphene.Boolean()
    avalible = graphene.Boolean()
    form = graphene.Field(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            name = args.get('name')
            db_name = args.get('db_name')
            tab_name = args.get('tab_name')

            if is_db_name_avalible(_db_name=db_name) is False:
                return CreateForm(form=None, avalible=False, ok=True)

            create_db_table(_db_name=db_name)
            new_form = create_ax_form(_name=name, _db_name=db_name)

            # Create default process
            # Add Admins role to object
            # Add admin group user to role
            # Add role to States - Start, Default state
            # Add role to Actions - Add record, Delete
            # Add default grid
            create_default_tab(new_form, tab_name)

            ok = True
            return CreateForm(form=new_form, avalible=True, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateForm.')
            raise


class UpdateForm(graphene.Mutation):
    """ Update AxForm """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        db_name = graphene.String()
        icon = graphene.String()
        tom_label = graphene.String()

    ok = graphene.Boolean()
    avalible = graphene.Boolean()
    db_name_changed = graphene.String()
    form = graphene.Field(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(args.get('guid'))
            ).first()
            db_name_changed = None
            if str(args.get('db_name')) != str(ax_form.db_name):
                db_name_changed = args.get('db_name')
                if is_db_name_avalible(_db_name=args.get('db_name')) is False:
                    return UpdateForm(
                        form=None,
                        avalible=False,
                        db_name_changed=None,
                        ok=True
                    )
                else:
                    ax_dialects.dialect.rename_table(
                        old=ax_form.db_name,
                        new=args.get('db_name'))

            ax_form.name = args.get('name')
            ax_form.db_name = args.get('db_name')
            ax_form.icon = args.get('icon')
            ax_form.tom_label = args.get('tom_label')
            ax_model.db_session.commit()

            ok = True
            return UpdateForm(
                form=ax_form,
                avalible=True,
                db_name_changed=db_name_changed,
                ok=ok
            )
        except Exception:
            logger.exception('Error in gql mutation - UpdateForm.')
            raise


class DeleteForm(graphene.Mutation):
    """-"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    forms = graphene.List(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            guid = args.get('guid')

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(guid)
            ).first()

            # s.execute("SET FOREIGN_KEY_CHECKS=0;")

            # Delete all AxFields, AxColumns, drop columns + field permissions
            # for f in ax_object.fields:
            #     ax_object.delete_field(f)

            # for a in ax_object.actions:
            #     s.delete(a)

            # for st in ax_object.states:
            #     s.delete(st)

            # for r in ax_object.roles:
            #     s.delete(r)

            # for v in ax_object.grids:
            #     s.delete(v)

            ax_dialects.dialect.drop_table(db_name=ax_form.db_name)
            ax_model.db_session.delete(ax_form)
            ax_model.db_session.commit()

            # s.execute("SET FOREIGN_KEY_CHECKS=1;")

            query = Form.get_query(info)  # SQLAlchemy query
            form_list = query.all()
            ok = True
            return DeleteForm(forms=form_list, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteForm.')
            raise


class CreateFolder(graphene.Mutation):
    """ Creates AxForm wich is folder """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()

    ok = graphene.Boolean()
    form = graphene.Field(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            name = args.get('name')

            ax_form = AxForm()
            ax_form.name = name
            ax_form.is_folder = True
            ax_model.db_session.add(ax_form)
            ax_model.db_session.commit()

            ok = True
            return CreateFolder(form=ax_form, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateFolder.')
            raise


class UpdateFolder(graphene.Mutation):
    """ Update AxForm wich is folder """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()

    ok = graphene.Boolean()
    form = graphene.Field(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            name = args.get('name')

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(guid)
            ).first()
            ax_form.name = name
            ax_model.db_session.commit()

            ok = True
            return CreateFolder(form=ax_form, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateFolder.')
            raise


class DeleteFolder(graphene.Mutation):
    """ Delete AxForm wich is folder """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    forms = graphene.List(Form)
    ok = graphene.Boolean()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            guid = args.get('guid')

            ax_folder = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(guid)
            ).first()

            sub_objects = ax_model.db_session.query(AxForm).filter(
                AxForm.parent == ax_folder.guid
            ).all()

            for sub in sub_objects:
                sub.parent = None
                sub.position = 1000

            ax_model.db_session.delete(ax_folder)
            ax_model.db_session.commit()

            query = Form.get_query(info)  # SQLAlchemy query
            form_list = query.all()
            ok = True
            return DeleteFolder(forms=form_list, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateFolder.')
            raise


class ChangeFormsPositions(graphene.Mutation):
    """Change position and parent fields of multiple forms"""
    class Arguments:  # pylint: disable=missing-docstring
        positions = graphene.List(PositionInput)

    ok = graphene.Boolean()
    forms = graphene.List(Form)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            positions = args.get('positions')
            for position in positions:
                db_form = ax_model.db_session.query(AxForm).filter(
                    AxForm.guid == uuid.UUID(position.guid)
                ).one()
                current_parent = None
                if position.parent != '#':
                    current_parent = uuid.UUID(position.parent)
                db_form.parent = current_parent
                db_form.position = position.position

            ax_model.db_session.commit()

            query = Form.get_query(info)  # SQLAlchemy query
            form_list = query.all()
            ok = True
            return ChangeFormsPositions(forms=form_list, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - ChangeFormsPositions.')
            raise


class HomeQuery(graphene.ObjectType):
    """AxForm queryes"""
    all_forms = graphene.List(Form)

    async def resolve_all_forms(self, info):
        """Get all users"""
        try:
            query = Form.get_query(info)  # SQLAlchemy query
            form_list = query.all()
            await ax_cache.cache.set('form_list', form_list)
            return form_list
        except Exception:
            logger.exception('Error in GQL query - resolve_all_forms.')
            raise


class HomeMutations(graphene.ObjectType):
    """Contains all AxForm mutations"""
    create_form = CreateForm.Field()
    update_form = UpdateForm.Field()
    delete_form = DeleteForm.Field()
    create_folder = CreateFolder.Field()
    update_folder = UpdateFolder.Field()
    delete_folder = DeleteFolder.Field()
    change_forms_positions = ChangeFormsPositions.Field()
