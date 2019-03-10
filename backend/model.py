"""Axy Class Model
Contains class structure of Ax storage.
"""

import uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
# Boolean, Integer,
from sqlalchemy import Text, String, CHAR, LargeBinary, Float, Unicode
from sqlalchemy import TypeDecorator, Column
from sqlalchemy.dialects.postgresql import UUID
# from loguru import logger

engine = create_engine('sqlite:///ax_sqllite.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


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


# class AxFieldType(Base):
#     __tablename__ = '_ax_field_types'
#     uuid = Column(GUID(), primary_key=True,
#                   default=uuid.uuid4, unique=True, nullable=False)
#     name = Column(String(255))
#     default_name = Column(String(255))
#     default_db_name = Column(String(255))
#     order = Column(Integer())
#     value_type = Column(String(255))
#     web_element = Column(String(255))
#     comparator = Column(String(255))
#     is_group = Column(Boolean, unique=False, default=False)
#     field_group_name = Column(String(255))
#     icon = Column(String(255))
#     is_inline_editable = Column(Boolean, unique=False, default=False)
#     is_backend_available = Column(Boolean, unique=False, default=False)
#     is_updated_always = Column(Boolean, unique=False, default=False)
#     is_always_whole_row = Column(Boolean, unique=False, default=False)

#     def serialize(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'order': self.order,
#             'web_element': self.web_element,
#             'group': self.group,
#             'is_inline_editable': self.is_inline_editable,
#             'is_always_whole_row': self.is_always_whole_row
#         }
