"""Miscellaneous functions
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import graphene
import graphene_sqlalchemy
import pytz
import yaml
from loguru import logger

this = sys.modules[__name__]
root_path = None
timezone = None


def init_misc(timezone_name: str) -> None:
    """Inititate time_zone, root_path"""
    if timezone_name not in pytz.common_timezones:
        logger.error(
            'Timezone {tz} not valid. Falling back to UTC.', tz=timezone_name)
        this.timezone = 'UTC'

    this.timezone = pytz.timezone(timezone_name)


def date(_date: datetime = datetime.now()) -> datetime:
    """Localise python datetime"""
    localized_date = this.timezone.localize(_date, is_dst=None)
    return localized_date


def path(_path: str = '') -> str:
    """Get correct absolute path.

    Agrs:
        _path (str, optional): Defaults to ''. Path relative to module root.

    Returns:
        str: Absolute path to specified file or directory
    Examples:
        Access module files like path('backend/schemas/user_schema.py')
    """
    if this.root_path is None:
        this.root_path = Path(__file__).resolve().parent.parent
        logger.debug('File path = {root}', root=Path(__file__))
    return root_path / _path


def load_configuration() -> None:
    """Function that loads ax application configuration from app.yaml

    If application is running on Google App Engine, all params from
    env_variables section of app.yaml will be loaded as enviroment variables.
    If application is running outside of App Engine then we must load
    variables ourselves.

    Args:
        app_yaml_location (str): Path to app.yaml location.

    Returns:
        bool: The return value. True for success.
    Examples:
        Access configuration variables like os.environ['AX_VERSION']

    Raises:
        FileNotFoundError: Cant find app.yaml
        ValueError: Cant parse app.yaml
        LookupError: No env_variables section in app.yaml
    """
    app_yaml = path('app.yaml')

    if not os.path.isfile(app_yaml):
        raise FileNotFoundError('Configuration failed, app.yaml not found')
    if not os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine"):
        with open(app_yaml, 'r') as stream:
            try:
                yaml_vars = yaml.safe_load(stream)
                if 'env_variables' not in yaml_vars:
                    err = 'Configuration failed, no env_variables in app.yaml'
                    logger.error(err)
                    raise LookupError(err)
                for key, value in yaml_vars['env_variables'].items():
                    if value:
                        os.environ[key] = str(value)
            except yaml.YAMLError as exc:
                err = 'Configuration failed, cant parse yaml - ' + exc
                logger.error(err)
                raise ValueError(err)


def convert_column_to_string(type, column, registry=None):  # pylint: disable=redefined-builtin
    """This functions is needed to convert UUID column to String column
    for SQL Alchemy"""
    del type, registry
    return graphene.String(
        description=graphene_sqlalchemy.converter.get_column_doc(column),
        required=not(graphene_sqlalchemy.converter.is_column_nullable(column))
    )
