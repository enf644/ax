"""Initiate SQL dialects"""
import sys
from loguru import logger

this = sys.modules[__name__]
dialect_name = None
dialect = None


class SqliteDialect(object):
    """SQL query for Sqlite database"""

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'ALTER TABLE {old} RENAME TO {new};'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'


class PorstgreDialect(object):
    """SQL query for Postgre SQL database"""

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'ALTER TABLE {old} RENAME TO {new};'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'


class MysqlDialect(object):
    """SQL query for Mysql database"""

    def rename_table(self, old: str, new: str) -> str:
        """Rename table"""
        return f'RENAME TABLE `{old}` TO `{new}`'

    def drop_table(self, db_name: str) -> str:
        """Drop table"""
        return f'DROP TABLE {db_name};'


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
