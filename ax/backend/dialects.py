"""Initiate SQL dialects"""
import sys
from loguru import logger

this = sys.modules[__name__]
dialect_name = None
dialect = None


class SqliteDialect(object):
    """SQL query for Sqlite database"""

    def get_type(self, type_name):
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

    def create_data_table(self, db_name) -> str:
        """Create table with system columns"""
        sql = f"""CREATE TABLE {db_name} (
            guid VARCHAR PRIMARY KEY,
            ax_num INTEGER NOT NULL,
            ax_state VARCHAR NOT NULL
        );"""
        return sql

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'ALTER TABLE {old} RENAME TO {new};'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'

    def add_column(self, table, db_name, type_name):
        """Add column"""
        dialect_type = self.get_type(type_name=type_name)
        return f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"


class PorstgreDialect(object):
    """SQL query for Postgre SQL database"""

    def get_type(self, type_name):
        """Get dialect specific type"""
        sqlite_types = {
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

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'ALTER TABLE {old} RENAME TO {new};'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'

    def add_column(self, table, db_name, type_name):
        """Add column"""
        dialect_type = self.get_type(type_name=type_name)
        return f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"


class MysqlDialect(object):
    """SQL query for Mysql database"""

    def get_type(self, type_name):
        """Get dialect specific type"""
        sqlite_types = {
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

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'RENAME TABLE `{old}` TO `{new}`'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'

    def add_column(self, table, db_name, type_name):
        """Add column"""
        dialect_type = self.get_type(type_name=type_name)
        return f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"


def init_dialects(_dialect_name: str) -> None:
    """Initiate sql queries for right dialect"""
    try:
        this.dialect_name = _dialect_name
        if _dialect_name == 'sqlite':
            this.dialect = SqliteDialect()
        elif _dialect_name == 'postgre':
            this.dialect = PorstgreDialect()
        elif _dialect_name == 'mysql':
            this.dialect = MysqlDialect()
        else:
            raise Exception('Unknown dialect = ' + _dialect_name)

    except Exception:
        logger.exception('Error initiating dialects')
        raise
