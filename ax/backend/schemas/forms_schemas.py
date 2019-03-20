"""Describes schemas for AxForm manipulation"""
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from sqlalchemy import MetaData
from loguru import logger

from backend.misc import convert_column_to_string
from backend.model import AxForm, GUID
import backend.model as ax_model
import backend.cache as ax_cache

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


def create_table(_db_name: str) -> None:
    """Create database table"""
    try:
        ax_model.get_form_data_table(
            _db_name).__table__.create(bind=ax_model.engine)

    except Exception:
        logger.exception('Error creating new Form. Cant create db table')
        raise


def create_form(_name: str, _db_name: str) -> object:
    """Creates AxForm object"""
    try:
        ax_form = AxForm()
        ax_form.name = _name
        ax_form.db_name = _db_name
        ax_form.tom_view = "{{form_name}} - {{id}}"
        ax_form.icon = "clone"
        ax_model.db_session.add(ax_form)
        ax_model.db_session.commit()
        return ax_form
    except Exception:
        logger.exception('Error creating AxForm object')
        raise


class Form(SQLAlchemyObjectType):  # pylint: disable=missing-docstring
    class Meta:  # pylint: disable=missing-docstring
        model = AxForm
        interfaces = (relay.Node, )


class CreateForm(graphene.Mutation):
    """ Creates AxForm """
    class Arguments:  # pylint: disable=missing-docstring
        name = graphene.String()
        db_name = graphene.String()

    ok = graphene.Boolean()
    avalible = graphene.Boolean()
    form = graphene.Field(Form)

    async def mutate(self, info, **args):
        """Mutation logic"""
        try:
            del info
            name = args.get('name')
            db_name = args.get('db_name')

            if is_db_name_avalible(_db_name=db_name) is False:
                return CreateForm(form=None, avalible=False, ok=True)

            create_table(_db_name=db_name)
            new_form = create_form(_name=name, _db_name=db_name)

            # Create default process
            # Add Admins role to object
            # Add admin group user to role
            # Add role to States - Start, Default state
            # Add role to Actions - Add record, Delete
            # Add default grid
            # Add default tab

            ok = True
            return CreateForm(form=new_form, avalible=True, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateForm.')
            raise


class FormsQuery(graphene.ObjectType):
    """AxForm queryes"""
    form = SQLAlchemyConnectionField(Form)
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


class FormMutations(graphene.ObjectType):
    """Contains all AxForm mutations"""
    create_form = CreateForm.Field()
