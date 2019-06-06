"""Axy Class Model
Contains class structure of Ax storage.
"""
import sys
import uuid
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import Text, String, CHAR, Float, Unicode, Boolean, Integer
from sqlalchemy import TypeDecorator, Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from loguru import logger
import backend.misc as ax_misc


# TODO: replace String(2000) for json fields with dialect agnostic JSON field

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


class AxForm(Base):
    """Stores Ax-Forms"""
    __tablename__ = '_ax_forms'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    db_name = Column(String(255))
    parent = Column(GUID())
    position = Column(Integer())
    fields = relationship(
        "AxField", order_by="AxField.position", cascade="all, delete-orphan")
    grids = relationship("AxGrid", order_by="AxGrid.position")
    states = relationship("AxState", cascade="all, delete-orphan")
    actions = relationship("AxAction", cascade="all, delete-orphan")
    roles = relationship("AxRole", cascade="all, delete-orphan")
    tom_label = Column(String(255))
    icon = Column(String(255))
    is_folder = Column(Boolean, unique=False, default=False)
    row_guid = None
    current_state_name = ""
    current_state_object = None
    from_state_name = ""
    from_state_object = None
    avalible_actions = None
    permissions = relationship(
        "AxRoleFieldPermission", cascade="all, delete-orphan")

    @property
    def db_fields(self):
        """Only AxFields that are database columns"""
        db_fields = []
        for field in self.fields:
            if field.is_tab is False and field.field_type.value_type != "VIRTUAL":
                db_fields.append(field)
        return db_fields

    def get_row_data(self):
        """Set current AxForm to match specific row in database table"""
        return "GET ROW DATA"

# class AxFormData():
#     """Dummy for each AxForm instance"""
#     guid = Column(GUID(), primary_key=True,
#                   default=uuid.uuid4, unique=True, nullable=False)
#     ax_num = Column(Integer())
#     ax_state = Column(String(255))


# def get_form_data_table(_db_name):
#     """Returns dummy for new AxForm db table"""
#     classname = "AxForm_" + _db_name
#     result_table = type(classname, (Base, AxFormData),
#                         {'__tablename__': _db_name})
#     return result_table


class AxFieldType(Base):
    """List of avalible ax field types"""
    __tablename__ = '_ax_field_types'
    tag = Column(String(64), primary_key=True, unique=True)
    name = Column(String(255))
    parent = Column(String(64))
    position = Column(Integer())
    default_name = Column(String(255))
    default_db_name = Column(String(255))
    value_type = Column(String(255))
    comparator = Column(String(255))
    icon = Column(String(255))
    is_group = Column(Boolean, unique=False, default=False)
    is_inline_editable = Column(Boolean, unique=False, default=False)
    is_backend_available = Column(Boolean, unique=False, default=False)
    is_setting_avalible = Column(Boolean, unique=False, default=False)
    is_columnn_avalible = Column(Boolean, unique=False, default=False)
    is_updated_always = Column(Boolean, unique=False, default=False)
    is_always_whole_row = Column(Boolean, unique=False, default=False)

    def __init__(self,
                 tag, name=None,
                 position=0,
                 default_name=None,
                 default_db_name="",
                 value_type="",
                 parent="",
                 icon="",
                 comparator="",
                 is_inline_editable=False,
                 is_backend_available=False,
                 is_setting_avalible=False,
                 is_columnn_avalible=False,
                 is_updated_always=False,
                 is_group=False,
                 is_always_whole_row=False
                 ):
        self.tag = tag
        self.name = name
        self.position = position
        self.default_name = default_name
        self.default_db_name = default_db_name
        self.value_type = value_type
        self.parent = parent
        self.is_group = is_group
        self.comparator = comparator
        self.icon = icon
        self.is_inline_editable = is_inline_editable
        self.is_backend_available = is_backend_available
        self.is_setting_avalible = is_setting_avalible
        self.is_columnn_avalible = is_columnn_avalible
        self.is_updated_always = is_updated_always
        self.is_always_whole_row = is_always_whole_row


class AxField(Base):
    """List of fields in each form"""
    __tablename__ = '_ax_fields'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    name = Column(String(255))
    db_name = Column(String(255))
    position = Column(Integer())
    options_json = Column(String(2000))
    # value_type = Column(String(255)) TODO Check if needed
    field_type_tag = Column(String(64), ForeignKey('_ax_field_types.tag'))
    field_type = relationship("AxFieldType")
    is_tab = Column(Boolean, unique=False, default=False)
    is_required = Column(Boolean, unique=False, default=False)
    is_whole_row = Column(Boolean, unique=False, default=False)
    parent = Column(GUID())
    value = None
    is_readonly = False
    needs_sql_update = False

    @property
    def is_virtual(self):
        """Is current fieldtype is Virtual (calculated field)"""
        if self.field_type.value_type == "VIRTUAL":
            return True
        else:
            return False


class Ax1tomReference(Base):
    """Stores 1 to M fields relation"""
    __tablename__ = '_ax_mtom_references'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    field_guid = Column(GUID(), ForeignKey('_ax_fields.guid'))
    row_guid = Column(GUID())
    child_guid = Column(GUID())


class AxGrid(Base):
    """Stores Ax grids"""
    __tablename__ = '_ax_grids'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    db_name = Column(String(255))
    position = Column(Integer())
    options_json = Column(String(2000))
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    is_default_view = Column(Boolean)
    columns = relationship(
        "AxColumn", order_by="AxColumn.position", cascade="all, delete-orphan")


class AxColumn(Base):
    """Stores columns for each grid"""
    __tablename__ = '_ax_columns'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    position = Column(Integer())
    options_json = Column(String(2000))
    field_guid = Column(GUID(), ForeignKey('_ax_fields.guid'))
    field = relationship("AxField")
    grid_guid = Column(GUID(), ForeignKey('_ax_grids.guid'))
    grid = relationship("AxGrid")
    column_type = Column(String(50))
    aggregation_type = Column(String(50), nullable=True)


class AxGroup2Users(Base):
    """Stores info on groups and users relation. What users are in group X."""
    __tablename__ = '_ax_group2user'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    group_guid = Column(GUID(), ForeignKey('_ax_users.guid'))
    user_guid = Column(GUID(), ForeignKey('_ax_users.guid'))


class AxUser(Base):
    """Describes Ax users."""
    __tablename__ = '_ax_users'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(Text)
    email = Column(Text)
    password = Column(String(255))
    is_group = Column(Boolean, unique=False, default=False)
    is_admin = Column(Boolean, unique=False, default=False)
    is_everyone = Column(Boolean, unique=False, default=False)
    is_all_users = Column(Boolean, unique=False, default=False)
    is_anon = Column(Boolean, unique=False, default=False)
    parent = Column(GUID())
    position = Column(Integer)
    users = relationship(
        "AxUser",
        secondary='_ax_group2user',
        primaryjoin="AxUser.guid==AxGroup2Users.group_guid",
        secondaryjoin="AxUser.guid==AxGroup2Users.user_guid",
        backref="users_in_group"
    )


class AxRole2Users(Base):
    """What users and groups are assigned to Role?"""
    __tablename__ = '_ax_role2user'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    role_guid = Column(GUID(), ForeignKey('_ax_roles.guid'))
    user_guid = Column(GUID(), ForeignKey('_ax_users.guid'))


class AxRole(Base):
    """Stores Roles for each workflow"""
    __tablename__ = '_ax_roles'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    users = relationship("AxUser", secondary='_ax_role2user')
    icon = Column(String(255))
    is_admin = Column(Boolean, unique=False, default=False)


class AxState2Role(Base):
    """Stores Roles that are assigned for state of workflow"""
    __tablename__ = '_ax_state2role'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    state_guid = Column(GUID(), ForeignKey('_ax_states.guid'))
    role_guid = Column(GUID(), ForeignKey('_ax_roles.guid'))


class AxState(Base):
    """Stores states for each workflow"""
    __tablename__ = '_ax_states'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    roles = relationship("AxRole", secondary='_ax_state2role')
    is_start = Column(Boolean, unique=False, default=False)
    is_deleted = Column(Boolean, unique=False, default=False)
    is_all = Column(Boolean, unique=False, default=False)
    x = Column(Float)
    y = Column(Float)


class AxAction2Role(Base):
    """What roles are assigned for each action of workflow"""
    __tablename__ = '_ax_action2role'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    action_guid = Column(GUID(), ForeignKey('_ax_actions.guid'))
    role_guid = Column(GUID(), ForeignKey('_ax_roles.guid'))


class AxAction(Base):
    """Stores actions for each workflow"""
    __tablename__ = '_ax_actions'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    roles = relationship("AxRole", secondary='_ax_action2role')
    from_state_guid = Column(GUID(), ForeignKey('_ax_states.guid'))
    to_state_guid = Column(GUID(), ForeignKey('_ax_states.guid'))
    from_state = relationship('AxState', foreign_keys=[from_state_guid])
    to_state = relationship('AxState', foreign_keys=[to_state_guid])
    code = Column(Text(convert_unicode=True))
    confirm_text = Column(String(255))
    close_modal = Column(Boolean, unique=False, default=True)
    icon = Column(String(255))
    radius = Column(Float)


class AxRoleFieldPermission(Base):
    """What role can view fields on each state of workflow"""
    __tablename__ = '_ax_role_field_permissions'
    guid = Column(GUID(), primary_key=True,
                  default=uuid.uuid4, unique=True, nullable=False)
    form_guid = Column(GUID(), ForeignKey('_ax_forms.guid'))
    form = relationship("AxForm")
    role_guid = Column(GUID(), ForeignKey('_ax_roles.guid'))
    role = relationship("AxRole")
    state_guid = Column(GUID(), ForeignKey('_ax_states.guid'))
    state = relationship("AxState")
    field_guid = Column(GUID(), ForeignKey('_ax_fields.guid'))
    field = relationship("AxField")
    read = Column(Boolean, unique=False, default=False)
    edit = Column(Boolean, unique=False, default=False)
