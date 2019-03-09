"""Module for database migration using Alembic"""
import os
import sys
from alembic.config import Config
from alembic import command
import backend.model as ax_model
from backend.model import AxAlembicVersion


def create_database() -> bool:
    """Create database and create baseline version in Alembic"""
    try:
        ax_model.Base.metadata.create_all(ax_model.engine)
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, "baseline")
        command.stamp(alembic_cfg, "head")
        return True
    except Exception as exc:
        raise Exception('Failed /install ->  ' + exc)


def init_migration():
    """Check current version of Database.
    Run create database if not yet created"""
    if ax_model.engine.dialect.has_table(
            ax_model.engine,
            '_ax_alembic_version'):
        current_version = ax_model.db_session.query(AxAlembicVersion).first()
        print('Current DB version: ' + str(current_version.version_num))
    else:
        create_database()
        os.execv(sys.executable, ['python'] + sys.argv)
