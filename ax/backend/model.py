"""Axy Class Model
Contains class structure of Ax storage.
"""
import sys
import uuid
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Text, String, CHAR, Float, Unicode, Boolean, Integer
from sqlalchemy import TypeDecorator, Column, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from loguru import logger
import backend.misc as ax_misc

this = sys.modules[__name__]
engine = None
db_session = None
db_url = None
Base = declarative_base()


def init_model(dialect: str, host: str, port: str, login: str, password: str,
               database: str, sqlite_filename: str, sqlite_absolute_path: str
               ) -> None:
    """Initiate database model

    Args:
        dialect (str): Supported dialects: sqlite | mysql
        host (str): Database host
        port (str): Database port
        login (str): Database user
        password (str): Database user password
        database (str): Database schema name
        sqlite_filename (str): Sqlite database file name. (ax_sqlite.db)
        sqlite_absolute_path (str): Path to Sqlite file. If file does not exist
            it will be created
    """
    del host, port, login, password, database
    try:
        if dialect == 'sqlite':
            if sqlite_absolute_path is None:
                db_path = ax_misc.path(sqlite_filename)
                this.db_url = 'sqlite:///' + str(db_path)
            else:
                db_path = str(Path(sqlite_absolute_path) / sqlite_filename)
                this.db_url = 'sqlite:///' + db_path
        else:
            msg = 'This database dialect is not supported'
            logger.error(msg)
            raise Exception(msg)

        logger.debug('DB url = {url}', url=this.db_url)
        this.engine = create_engine(this.db_url, convert_unicode=True)
        this.db_session = scoped_session(sessionmaker(autocommit=False,
                                                      autoflush=False,
                                                      bind=this.engine))
        this.Base.query = this.db_session.query_property()
    except Exception:
        logger.exception('Error initating SqlAlchemy model')
        raise


class GUID(TypeDecorator):  # pylint: disable=W0223
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class AxAlembicVersion(Base):
    """Stores current Database version for alembic migration"""
    __tablename__ = '_ax_alembic_version'
    version_num = Column(String(255), primary_key=True)


class AxSchedulerJob(Base):
    """Table and metadata for apscheduler."""
    __tablename__ = '_ax_scheduler_jobs'
    id = Column(Unicode(191, _warn_on_bytestring=False), primary_key=True)
    next_run_time = Column(Float(25), index=True)
    job_state = Column(LargeBinary, nullable=False)


class AxUser(Base):
    """Describes Axy users."""

    __tablename__ = '_ax_users'
    # TODO set binary=True is database supports UUID
    uuid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(Text)
    email = Column(Text)
    username = Column(String(255))

    def serialize(self):
        """Serialize"""
        return {
            'uuid': self.uuid, 'name': self.name, 'db_name': self.db_name
        }


class AxFieldType(Base):
    """List of avalible ax field types"""
    __tablename__ = '_ax_field_types'
    uuid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    default_name = Column(String(255))
    default_db_name = Column(String(255))
    order = Column(Integer())
    value_type = Column(String(255))
    web_element = Column(String(255))
    comparator = Column(String(255))
    is_group = Column(Boolean, unique=False, default=False)
    field_group_name = Column(String(255))
    icon = Column(String(255))
    is_inline_editable = Column(Boolean, unique=False, default=False)
    is_backend_available = Column(Boolean, unique=False, default=False)
    is_updated_always = Column(Boolean, unique=False, default=False)
    is_always_whole_row = Column(Boolean, unique=False, default=False)

    def serialize(self):
        """Serialize"""
        return {
            'id': self.id,
            'name': self.name,
            'order': self.order,
            'web_element': self.web_element,
            'group': self.group,
            'is_inline_editable': self.is_inline_editable,
            'is_always_whole_row': self.is_always_whole_row
        }
