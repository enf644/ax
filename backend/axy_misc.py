"""Miscellaneous functions
"""

import os
import yaml
import graphene
import graphene_sqlalchemy

def load_configuration(app_yaml_location: str) -> bool:
    """Function that loads axy application configuration from app.yaml

    If application is running on Google App Engine, all params from
    env_variables section of app.yaml will be loaded as enviroment variables.
    If application is running outside of App Engine then we must load
    variables ourselves.

    Args:
        app_yaml_location (str): Path to app.yaml location.

    Returns:
        bool: The return value. True for success.
    Examples:
        Access configuration variables like os.environ['AXY_VERSION']

    Raises:
        FileNotFoundError: Cant find app.yaml
        ValueError: Cant parse app.yaml
        LookupError: No env_variables section in app.yaml
    """
    app_yaml = os.path.join(app_yaml_location, '', 'app.yaml')
    if not os.path.isfile(app_yaml):
        raise FileNotFoundError('Configuration failed, app.yaml not found')
    if not os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine"):
        with open(app_yaml, 'r') as stream:
            try:
                yaml_vars = yaml.safe_load(stream)
                if 'env_variables' not in yaml_vars:
                    raise LookupError('Configuration failed, no env_variables '
                                      'in app.yaml')
                for key, value in yaml_vars['env_variables'].items():
                    os.environ[key] = value
            except yaml.YAMLError as exc:
                raise ValueError('Configuration failed, '
                                 'cant parse yaml - ' + exc)
    return True


def convert_column_to_string(type, column, registry=None):  # pylint: disable=redefined-builtin
    """This functions is needed to convert UUID column to String column
    for SQL Alchemy"""
    del type, registry
    return graphene.String(
        description=graphene_sqlalchemy.converter.get_column_doc(column),
        required=not(graphene_sqlalchemy.converter.is_column_nullable(column))
    )
