"""Module for database migration using Alembic"""
import os
import sys
from loguru import logger
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from alembic import command
import backend.model as ax_model
import backend.misc as ax_misc
from backend.model import AxAlembicVersion

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
    try:
        if os.environ.get('AX_DB_REVISION') is None:
            msg = 'Cant find AX_DB_REVISION in enviroment variables or app.yaml'
            logger.error(msg)
            raise Exception(msg)

        ax_model.Base.metadata.create_all(ax_model.engine)
        first_version = AxAlembicVersion()
        first_version.version_num = os.environ.get('AX_DB_REVISION')
        ax_model.db_session.add(first_version)
        ax_model.db_session.commit()

        logger.info('Ax tables not found. Creating database tables.')
        return True
    except Exception:
        logger.exception('Failed creating ax database tables')
        raise


def database_fits_metadata() -> None:
    """Compare metada and database"""
    try:
        with ax_model.engine.connect() as active_connection:
            context = MigrationContext.configure(active_connection)
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
    else:
        if database_fits_metadata() is False:
            upgrade_database()
