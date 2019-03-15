"""Create new version of Ax

Usage:
  publish_version.py [--major] [--minor] [--no-front]

Options:
  --major       Increment major version
  --minor       Increment minor version
  --no-front    Skip npm run build

"""

import os
import sys
import uuid
import subprocess
from pathlib import Path
import ruamel.yaml
from loguru import logger
from docopt import docopt
from alembic import command

setup_path = Path(__file__).parent.resolve()
ax_path = setup_path / 'ax'
frontend_path = setup_path / 'ax' / 'frontend'
sys.path.insert(0, str(ax_path))

# pylint: disable=wrong-import-position
import ax.backend.misc as ax_misc
import ax.backend.model as ax_model
import ax.backend.migration as ax_migration
import ax.main as ax_app
from backend.model import AxAlembicVersion
# pylint: enable=wrong-import-position

this = sys.modules[__name__]

app_yaml = None
app_yaml_path = None
final_version = None
revision_id = None
yaml = ruamel.yaml.YAML()


def init_ax():
    """Load config and init model"""
    try:
        ax_misc.load_configuration()
        ax_app.init_model()
        ax_migration.init_alembic_config()
    except Exception:
        logger.exception('Error getting ax settings')
        raise


def bump_version(is_major: bool = False, is_minor: bool = False):
    """Increment ax version in app.yaml"""
    try:
        this.app_yaml_path = Path(
            __file__).parent.resolve() / 'ax' / 'app.yaml'

        with open(this.app_yaml_path) as yaml_file:
            this.app_yaml = yaml.load(yaml_file)
            version_string = this.app_yaml['env_variables']['AX_VERSION']
            (major, minor, micro) = [int(s) for s in version_string.split('.')]

            micro += 1
            if is_minor:
                minor += 1
                micro = 0
            if is_major:
                major += 1
                minor = 0
                micro = 0

            this.final_version = str(major) + "." + \
                str(minor) + "." + str(micro)
            this.app_yaml['env_variables']['AX_VERSION'] = this.final_version

    except Exception:
        logger.exception('Failed to bump version')
        raise


def create_db_revision():
    """Genereting alembic database migration script"""
    try:
        logger.info('Database does not fit metadata. Creating revision')
        rand = int(uuid.uuid4()) % 100000000000000
        rand_str = str(hex(rand)[2:-1])
        this.revision_id = 'v' + this.final_version + '_' + rand_str
        message = ''
        label = 'v' + this.final_version
        command.revision(
            ax_migration.alembic_cfg,
            message,
            rev_id=this.revision_id,
            autogenerate=True,
            branch_label=label
        )
        this.app_yaml['env_variables']['AX_DB_REVISION'] = this.revision_id

    except Exception:
        logger.exception('Error in creating database revision')
        raise


def save_db_revision() -> None:
    """Saves db revision to current database"""
    try:
        current_version = AxAlembicVersion()
        current_version.version_num = this.revision_id
        ax_model.db_session.add(current_version)
        ax_model.db_session.commit()
    except Exception:
        logger.exception('Failed saving revision id to database')
        raise


def clear_pipy_dist() -> None:
    """Deletes all previos compiled packages"""
    try:
        filelist = [f for f in os.listdir(str(this.setup_path / 'dist'))]
        for file in filelist:
            os.remove(os.path.join(str(this.setup_path / 'dist'), file))
    except Exception:
        logger.exception('Failed clearing /dist folder')
        raise


def npm_run_build() -> None:
    """Build frontend with webpack"""
    try:
        cmd = 'npm run build'
        subprocess.check_call(cmd, shell=True, cwd=str(this.frontend_path))
    except Exception:
        logger.exception('Failed building frontend with npm run build')
        raise


def buid_pypi() -> None:
    """Runs setup.py and builds ax package"""
    try:
        cmd = 'python setup.py sdist bdist_wheel'
        subprocess.check_call(cmd, shell=True, cwd=str(this.setup_path))
    except Exception:
        logger.exception('Failed building pypi package')
        raise


def save_yaml() -> None:
    """Saves yaml file to disk"""
    try:
        with open(this.app_yaml_path, "w") as yaml_file:
            yaml.dump(this.app_yaml, yaml_file)
    except Exception:
        logger.exception('Error saving changes to app.yaml file')
        raise


def upload_to_pypi() -> None:
    """Upload package to pypi with `twine upload`"""
    try:
        cmd = 'twine upload dist/*'
        subprocess.check_call(cmd, shell=True, cwd=str(this.setup_path))
    except Exception:
        logger.exception('Uploading to pypi failed')
        raise


def tag_git() -> None:
    """Tags current git commit"""
    try:
        cmd = 'git tag ' + this.final_version + \
            ' -a -m \'Release ' + this.final_version + '\''
        subprocess.check_call(cmd, shell=True, cwd=str(this.setup_path))
    except Exception:
        logger.exception('Failed git tag')
        raise


if __name__ == "__main__":
    arguments = docopt(__doc__)
    logger.info(arguments['--minor'])

    #  Init migration.py for alembic and model.py for database
    init_ax()

    #  Automatic bump version, save in app.yaml
    bump_version(is_major=arguments['--major'], is_minor=arguments['--minor'])

    #  Create db migration script
    if ax_migration.database_fits_metadata() is False:
        # Create migration script and save revision on app.yaml
        create_db_revision()
        save_db_revision()
    else:
        logger.info('No database changes detected')

    save_yaml()
    clear_pipy_dist()

    if arguments['--no-front'] is False:
        npm_run_build()

    buid_pypi()
    upload_to_pypi()
    tag_git()

    #  Publish pipy package to TEST pypi
    #  Run all tests
    #  Tag git commit
    #  Publish to real pypi
