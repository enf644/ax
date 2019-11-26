"""
Module for database migration using Alembic
It checks if database is accesible.
Creates sqlite database if needed.
Checks if database have SqlAlchemy tables. If not - it creates tables.
    When tables are created, they are filled with default values.
    Such as AxFieldType are filled with field types.
Checks that current Database schema fits SqlAlchemy schema. If it is not,
    it tryes to upgrade it by running alembic migration scripts.

"""
import os
import sys
from loguru import logger
from passlib.hash import pbkdf2_sha256
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from alembic import command
import backend.model as ax_model
import backend.misc as ax_misc
from backend.model import AxAlembicVersion, AxFieldType, AxUser, AxGroup2Users,\
    AxPage

this = sys.modules[__name__]
alembic_cfg = None


def init_alembic_config() -> None:
    """Create Alembic config"""
    try:
        ini_path = ax_misc.path("alembic.ini")
        this.alembic_cfg = Config(ini_path)
        alembic_folder = ax_misc.path("backend/alembic")
        this.alembic_cfg.set_main_option(
            'script_location', str(alembic_folder))
    except Exception:
        logger.exception('Error initating alembic config.')
        raise


def tables_exist() -> bool:
    """Checks if database tables are created"""
    try:
        tables_created = ax_model.engine.dialect.has_table(
            ax_model.engine, '_ax_alembic_version')
        if tables_created:
            return True
        else:
            return False
    except Exception:
        logger.exception('Error in detecting if database tables are created')
        raise


def create_tables() -> None:
    """Create database and create baseline version in Alembic"""
    with ax_model.scoped_session("migration -> create_tables") as db_session:
        if os.environ.get('AX_DB_REVISION') is None:
            msg = 'Cant find AX_DB_REVISION in enviroment variables or app.yaml'
            logger.error(msg)
            raise Exception(msg)

        # ax_model.Base.query = db_session.query_property()
        ax_model.Base.metadata.create_all(ax_model.engine)
        first_version = AxAlembicVersion()
        first_version.version_num = os.environ.get('AX_DB_REVISION')
        db_session.add(first_version)

        logger.info('Ax tables not found. Creating database tables.')
        return True


def create_default_pages():
    """ Create default page """
    with ax_model.scoped_session(
            "migration -> create_default_pages") as db_session:
        index_page = AxPage()
        index_page.name = "Index Page"
        index_page.code = (f"<h1>Welcome to Ax pages</h1>\n"
                           f"<br/><br/>Hello world")
        db_session.add(index_page)
        db_session.commit()


def create_default_users():
    """ Create Admin group, Default admin, Everyone, All users """
    msg = "Error -> Migration -> create_default_users"
    with ax_model.scoped_session(msg) as db_session:
        # Admin group
        admin_group = AxUser()
        # admin_group.short_name = 'users.admin-group-name'
        admin_group.short_name = 'Administrators'
        admin_group.is_group = True
        admin_group.is_admin = True
        db_session.add(admin_group)

        # Default admin
        admin = AxUser()
        admin.email = 'default@ax-workflow.com'
        admin.password = pbkdf2_sha256.hash('deleteme')
        admin.name = 'Default Administrator. Delete this user.'
        admin.short_name = 'Default Admin'
        db_session.add(admin)

        db_session.commit()

        group_user = AxGroup2Users()
        group_user.group_guid = admin_group.guid
        group_user.user_guid = admin.guid
        db_session.add(group_user)

        # Everyone
        everyone_group = AxUser()
        # everyone_group.short_name = 'users.everyone-group-name'
        everyone_group.short_name = 'Everyone'
        everyone_group.is_group = True
        everyone_group.is_everyone = True
        db_session.add(everyone_group)

        # All users
        all_group = AxUser()
        # all_group.short_name = 'users.all-users-group-name'
        all_group.short_name = 'All users'
        all_group.is_group = True
        all_group.is_all_users = True
        db_session.add(all_group)

        db_session.commit()


def create_field_types() -> None:
    """Fill AxFieldType with field types"""
    try:
        with ax_model.scoped_session() as db_session:
            # Identification
            db_session.add(AxFieldType(
                tag='group-id',
                is_group=True,
                position=1,
                icon="fas fa-key"))
            db_session.add(AxFieldType(
                tag="AxGuid",
                parent="group-id",
                default_db_name="rowGuid",
                position=1,
                is_virtual=True,
                virtual_source='guid',
                comparator="",
                icon="fas fa-key"))
            db_session.add(AxFieldType(
                tag='AxNum',
                parent="group-id",
                default_db_name="axNum",
                value_type="VARCHAR(255)",
                position=2,
                is_readonly=True,
                is_backend_available=True,
                icon="fas fa-sort-numeric-up"))

            # Process controll
            db_session.add(AxFieldType(
                tag='group-process',
                is_group=True,
                position=2,
                icon="fas fa-code-branch"))
            db_session.add(AxFieldType(
                tag="AxState",
                parent="group-process",
                default_db_name="rowState",
                position=1,
                is_virtual=True,
                virtual_source='axState',
                icon="fas fa-code-branch"))
            db_session.add(AxFieldType(
                tag="AxChangelog",
                parent="group-process",
                position=4,
                default_db_name="changelog",
                is_columnn_avalible=True,
                value_type="JSON",
                is_backend_available=True,
                is_readonly=True,
                is_updated_always=True,
                is_always_whole_row=True,
                icon="fas fa-code-branch"))

            # String
            db_session.add(AxFieldType(
                tag='group-string',
                is_group=True,
                position=3,
                icon="fas fa-font"))
            db_session.add(AxFieldType(
                tag="AxString",
                parent="group-string",
                default_db_name="string",
                position=1,
                value_type="VARCHAR(255)",
                is_inline_editable=True,
                icon="fas fa-font"))
            db_session.add(AxFieldType(
                tag="AxEmail",
                parent="group-string",
                default_db_name="email",
                position=2,
                value_type="VARCHAR(255)",
                is_inline_editable=True,
                icon="fas fa-font"))
            db_session.add(AxFieldType(
                tag="AxTelephone",
                parent="group-string",
                default_db_name="telephone",
                position=3,
                value_type="VARCHAR(255)",
                is_columnn_avalible=True,
                is_inline_editable=True,
                icon="fas fa-font"))

            # Decoration
            db_session.add(AxFieldType(
                tag='group-decoration',
                is_group=True,
                position=4,
                icon="fas fa-code"))
            db_session.add(AxFieldType(
                tag="AxHtml",
                parent="group-decoration",
                default_db_name="html",
                position=1,
                is_virtual=True,
                virtual_source='guid',
                is_display_backend_avalible=True,
                icon="fas fa-code"))

            # Text
            db_session.add(AxFieldType(
                tag='group-text',
                name="types.text",
                is_group=True,
                position=5,
                icon="fas fa-align-left"))
            db_session.add(AxFieldType(
                tag="AxText",
                parent="group-text",
                default_db_name="text",
                position=1,
                value_type="TEXT",
                is_inline_editable=True,
                is_columnn_avalible=True,
                icon="fas fa-align-left"))
            db_session.add(AxFieldType(
                tag="AxMarkdown",
                parent="group-text",
                default_db_name="markdown",
                position=2,
                value_type="TEXT",
                is_columnn_avalible=True,
                is_always_whole_row=True,
                icon="fas fa-align-left"))

            # Number
            db_session.add(AxFieldType(
                tag='group-number',
                is_group=True,
                position=6,
                icon="fas fa-hashtag"))
            db_session.add(AxFieldType(
                tag="AxInteger",
                parent="group-number",
                default_db_name="integer",
                position=1,
                value_type="INT",
                comparator="number",
                is_inline_editable=True,
                is_columnn_avalible=True,
                icon="fas fa-hashtag"))
            db_session.add(AxFieldType(
                tag="AxDecimal",
                parent="group-number",
                default_db_name="decimal",
                position=2,
                value_type="DECIMAL(65,2)",
                comparator="number",
                is_columnn_avalible=True,
                is_inline_editable=True,
                icon="fas fa-hashtag"))
            db_session.add(AxFieldType(
                tag="AxIntSlider",
                parent="group-number",
                default_db_name="intSlider",
                position=1,
                value_type="INT",
                comparator="number",
                is_inline_editable=True,
                icon="fas fa-hashtag"))

            # Boolean
            db_session.add(AxFieldType(
                tag='group-boolean',
                is_group=True,
                position=7,
                icon="fas fa-toggle-on"))
            db_session.add(AxFieldType(
                tag="AxCheckbox",
                parent="group-boolean",
                default_db_name="checkbox",
                position=1,
                value_type="BOOL",
                is_inline_editable=True,
                is_columnn_avalible=True,
                icon="fas fa-toggle-on"))
            db_session.add(AxFieldType(
                tag="AxSwitch",
                parent="group-boolean",
                default_db_name="switch",
                position=1,
                value_type="BOOL",
                is_inline_editable=True,
                is_columnn_avalible=True,
                icon="fas fa-toggle-on"))

            # Relationship
            db_session.add(AxFieldType(
                tag='group-relationship',
                is_group=True,
                position=8,
                icon="fas fa-link"))
            db_session.add(AxFieldType(
                tag="Ax1to1",
                parent="group-relationship",
                default_name="types.ax-1to1-default",
                default_db_name="toOne",
                position=1,
                value_type="GUID",
                is_inline_editable=False,
                is_columnn_avalible=True,
                icon="fas fa-link"))
            db_session.add(AxFieldType(
                tag="Ax1tom",
                parent="group-relationship",
                default_name="types.ax-1tom-default",
                default_db_name="toMany",
                position=2,
                value_type="JSON",
                is_backend_available=True,
                is_columnn_avalible=True,
                is_inline_editable=False,
                icon="fas fa-link"))
            db_session.add(AxFieldType(
                tag="Ax1tomTable",
                parent="group-relationship",
                default_name="types.ax-1tom-table-default",
                default_db_name="toManyTable",
                position=3,
                value_type="JSON",
                is_backend_available=True,
                is_columnn_avalible=True,
                is_inline_editable=True,
                icon="fas fa-link"))

            #Date and Time
            db_session.add(AxFieldType(
                tag='group-date',
                is_group=True,
                position=9,
                icon="fas fa-calendar"))
            db_session.add(AxFieldType(
                tag="AxDate",
                parent="group-date",
                default_db_name="date",
                position=1,
                value_type="TIMESTAMP",
                comparator="date",
                is_inline_editable=True,
                is_columnn_avalible=True,
                icon="fas fa-calendar"))

            # List
            db_session.add(AxFieldType(
                tag='group-list',
                is_group=True,
                position=10,
                icon="fas fa-list"))
            db_session.add(AxFieldType(
                tag="AxChoise",
                parent="group-list",
                default_db_name="choise",
                position=1,
                value_type="VARCHAR(255)",
                is_inline_editable=True,
                icon="fas fa-list"))
            db_session.add(AxFieldType(
                tag="AxRadio",
                parent="group-list",
                default_db_name="radio",
                position=1,
                value_type="VARCHAR(255)",
                is_inline_editable=True,
                icon="fas fa-list"))
            db_session.add(AxFieldType(
                tag="AxTags",
                parent="group-list",
                default_db_name="tags",
                position=1,
                value_type="JSON",
                is_inline_editable=True,
                icon="fas fa-list"))
            db_session.add(AxFieldType(
                tag="AxRadioSurvey",
                parent="group-list",
                default_db_name="survey",
                position=1,
                value_type="JSON",
                is_inline_editable=False,
                icon="fas fa-poll"))

            # Images
            db_session.add(AxFieldType(
                tag='group-images',
                is_group=True,
                position=11,
                icon="fas fa-image"))
            db_session.add(AxFieldType(
                tag="AxImageCropDb",
                parent="group-images",
                position=4,
                default_db_name="cropImage",
                is_backend_available=True,
                value_type="BLOB",
                icon="fas fa-image"))

            # Files
            db_session.add(AxFieldType(
                tag='group-files',
                is_group=True,
                position=12,
                icon="fas fa-file"))
            db_session.add(AxFieldType(
                tag="AxFiles",
                parent="group-files",
                position=1,
                default_db_name="files",
                value_type="JSON",
                is_backend_available=True,
                icon="fas fa-file"))

            # Users
            db_session.add(AxFieldType(
                tag='group-users',
                is_group=True,
                position=13,
                icon="fas fa-user"))
            db_session.add(AxFieldType(
                tag="AxUsers",
                parent="group-users",
                position=1,
                default_db_name="users",
                is_backend_available=True,
                is_columnn_avalible=True,
                value_type="JSON",
                icon="fas fa-user"))

            # Communication
            db_session.add(AxFieldType(
                tag='group-communication',
                is_group=True,
                position=14,
                icon="fas fa-comments"))
            db_session.add(AxFieldType(
                tag="AxComments",
                parent="group-communication",
                position=4,
                default_db_name="comments",
                value_type="GUID",
                is_backend_available=True,
                icon="fas fa-comments"))
            db_session.add(AxFieldType(
                tag="AxApproval",
                parent="group-communication",
                position=4,
                default_db_name="approval",
                value_type="JSON",
                is_backend_available=True,
                icon="fas fa-hands-helping"))

            # Payment
            db_session.add(AxFieldType(
                tag='group-payment',
                is_group=True,
                position=14,
                icon="fas fa-money-bill-alt"))
            db_session.add(AxFieldType(
                tag="AxPaymentStripe",
                parent="group-payment",
                position=4,
                default_db_name="stripe",
                value_type="JSON",
                is_backend_available=True,
                icon="fab fa-stripe-s"))
            db_session.add(AxFieldType(
                tag="AxPaymentYandex",
                parent="group-payment",
                position=4,
                default_db_name="kassa",
                value_type="JSON",
                is_backend_available=True,
                icon="fab fa-yandex"))

            db_session.commit()
    except Exception:
        logger.exception('Failed creating default AxFieldTypes')
        raise


def database_fits_metadata() -> None:
    """Compare metada and database"""
    try:
        with ax_model.engine.connect() as active_connection:
            context = MigrationContext.configure(active_connection)
            db_session = ax_model.Session()
            ax_model.Base.query = db_session.query_property()
            metadata = ax_model.Base.metadata
            diff = compare_metadata(context, metadata)
            return diff == []
    except Exception:
        logger.exception('Error in comparing metadata and database.')
        raise


def upgrade_database():
    """Run Alembic migration script and update db version"""
    try:
        logger.info('Database does not fit metadata. Upgrading database.')
        command.upgrade(this.alembic_cfg, "head")
        command.stamp(this.alembic_cfg, "head")
    except Exception:
        logger.exception('Error upgrading database with Alembic')
        raise


def init_migration():
    """Initiate migration module"""
    init_alembic_config()
    if tables_exist() is False:
        create_tables()
        create_field_types()
        create_default_users()
        create_default_pages()
    else:
        pass
        # if database_fits_metadata() is False:
        #     upgrade_database()
