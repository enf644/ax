"""Initiate SQL dialects"""
import sys
from loguru import logger
import sqlite3
import backend.model as ax_model
from backend.model import AxForm, AxField

this = sys.modules[__name__]
dialect_name = None
dialect = None


class SqliteDialect(object):
    """SQL query for Sqlite database"""
    name = 'sqlite'
    version = None

    def get_type(self, type_name) -> str:
        """Get dialect specific type"""
        sqlite_types = {
            'VIRTUAL': 'VIRTUAL',
            'TEXT': 'TEXT',
            'VARCHAR(255)': 'TEXT',
            'INT': 'INTEGER',
            'DECIMAL(65,2)': 'REAL',
            'BOOL': 'NUMERIC',
            'GUID': 'TEXT',
            'JSON': 'TEXT',
            'TIMESTAMP': 'INTEGER',
            'BLOB': 'BLOB'
        }
        return sqlite_types[type_name]

    def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid VARCHAR PRIMARY KEY,
                ax_num INTEGER NOT NULL,
                ax_state VARCHAR NOT NULL
            );"""
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'ALTER TABLE {old} RENAME TO {new};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise

    def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE {db_name};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise

    def add_column(self, table: str, db_name: str, type_name: str) -> None:
        """Add column"""
        try:
            dialect_type = self.get_type(type_name=type_name)
            sql = f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Sqlite allows rename of column only from version 3.25.0. 
        We have to reacreate table and copy data"""
        try:
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == table
            ).first()

            create_tmp = 'CREATE TABLE _ax_tmp (guid VARCHAR'
            for field in ax_form.db_fields:
                db_name = field.db_name if field.db_name != old_name else new_name
                db_type = self.get_type(field.field_type.value_type)
                create_tmp += f", {db_name}  {db_type}"

            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid'
            for field in ax_form.db_fields:
                copy_data += f", {field.db_name}"
            copy_data += f" FROM {ax_form.db_name};"

            drop_old = f"DROP TABLE {ax_form.db_name};"

            rename_tmp = f'ALTER TABLE _ax_tmp RENAME TO {ax_form.db_name};'

            try:
                ax_model.db_session.execute(create_tmp)
                ax_model.db_session.execute(copy_data)
                ax_model.db_session.execute(drop_old)
                ax_model.db_session.execute(rename_tmp)
                ax_model.db_session.commit()
            except Exception:
                ax_model.db_session.rollback()

            return True
        except Exception:
            logger.exception('Error executing SQL - rename_column')
            raise

    def drop_column(self, table, column) -> None:
        """Sqlite does not allows to drop columns.
        We have to reacreate table and copy data"""
        try:
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == table
            ).first()

            create_tmp = 'CREATE TABLE _ax_tmp (guid VARCHAR'
            for field in ax_form.db_fields:
                db_type = self.get_type(field.field_type.value_type)
                if field.db_name != column:
                    create_tmp += f", {field.db_name}  {db_type}"
            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid'
            for field in ax_form.db_fields:
                if field.db_name != column:
                    copy_data += f", {field.db_name}"
            copy_data += f" FROM {ax_form.db_name};"

            drop_old = f"DROP TABLE {ax_form.db_name};"

            rename_tmp = f'ALTER TABLE _ax_tmp RENAME TO {ax_form.db_name};'

            try:
                ax_model.db_session.execute(create_tmp)
                ax_model.db_session.execute(copy_data)
                ax_model.db_session.execute(drop_old)
                ax_model.db_session.execute(rename_tmp)
                ax_model.db_session.commit()
            except Exception:
                ax_model.db_session.rollback()

            return True
        except Exception:
            logger.exception('Error executing SQL - drop_column')
            raise


class PorstgreDialect(object):
    """SQL query for Postgre SQL database"""

    name = 'postgre'
    version = None

    def get_type(self, type_name):
        """Get dialect specific type"""
        postgre_types = {
            'VIRTUAL': 'VIRTUAL',
            'TEXT': 'TEXT',
            'VARCHAR(255)': 'VARCHAR(255)',
            'INT': 'INT',
            'DECIMAL(65,2)': 'DECIMAL(65,2)',
            'BOOL': 'BOOLEAN',
            'GUID': 'UUID',
            'JSON': 'JSON',
            'TIMESTAMP': 'TIMESTAMP',
            'BLOB': 'VARBIT'
        }
        return postgre_types[type_name]

    def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid UUID PRIMARY KEY,
                ax_num INTEGER NOT NULL,
                ax_state VARCHAR NOT NULL
            );"""
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'ALTER TABLE {old} RENAME TO {new};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise

    def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE {db_name};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise

    def add_column(self, table, db_name, type_name) -> None:
        """Add column"""
        try:
            dialect_type = self.get_type(type_name=type_name)
            sql = f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Rename column"""
        try:
            del type_name
            sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name};"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_column')
            raise

    def drop_column(self, table, column) -> None:
        """ Drop column """
        try:
            sql = f"ALTER TABLE {table} DROP COLUMN {column};"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_column')
            raise


class MysqlDialect(object):
    """SQL query for Mysql database"""

    name = 'mysql'
    version = None

    def get_type(self, type_name):
        """Get dialect specific type"""
        mysql_types = {
            'VIRTUAL': 'VIRTUAL',
            'TEXT': 'TEXT',
            'VARCHAR(255)': 'VARCHAR(255)',
            'INT': 'INT',
            'DECIMAL(65,2)': 'DECIMAL(65,2)',
            'BOOL': 'BOOL',
            'GUID': 'CHAR(32)',
            'JSON': 'TEXT',
            'TIMESTAMP': 'TIMESTAMP',
            'BLOB': 'BLOB'
        }
        return mysql_types[type_name]

    def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid VARCHAR(64) PRIMARY KEY,
                ax_num INT NOT NULL,
                ax_state VARCHAR(255) NOT NULL
            );"""
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'RENAME TABLE `{old}` TO `{new}`'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise

    def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE {db_name};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise

    def add_column(self, table, db_name, type_name) -> None:
        """Add column"""
        try:
            dialect_type = self.get_type(type_name=type_name)
            sql = f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Rename column"""
        try:
            dialect_type = self.get_type(type_name=type_name)
            sql = (
                f"ALTER TABLE `{table}` "
                f"CHANGE COLUMN `{old_name}` `{new_name}` {dialect_type}"
            )
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_column')
            raise

    def drop_column(self, table, column) -> None:
        """ Drop column """
        try:
            sql = f"ALTER TABLE {table} DROP COLUMN {column};"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_column')
            raise


def init_dialects(_dialect_name: str) -> None:
    """Initiate sql queries for right dialect"""
    try:
        this.dialect_name = _dialect_name
        if _dialect_name == 'sqlite':
            this.dialect = SqliteDialect()
            this.dialect.version = sqlite3.sqlite_version
        elif _dialect_name == 'postgre':
            this.dialect = PorstgreDialect()
        elif _dialect_name == 'mysql':
            this.dialect = MysqlDialect()
        else:
            raise Exception('Unknown dialect = ' + _dialect_name)

        logger.debug("Dialect initialised -> {dialect} -> {version}",
                     dialect=this.dialect.name, version=this.dialect.version)

    except Exception:
        logger.exception('Error initiating dialects')
        raise
