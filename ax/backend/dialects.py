"""Initiate SQL dialects"""
import sys
import sqlite3
import uuid
import re
from loguru import logger
import ujson as json
import backend.model as ax_model
from backend.model import AxForm

this = sys.modules[__name__]
dialect_name = None
dialect = None


def get_tom_sql(form_db_name, form_name, tom_label, fields):
    """ Constructs sql string form select query resulting to-M-label of row"""
    tags = re.findall("{{(.*?)}}", tom_label)
    true_tags = []
    for field in fields:
        if field.db_name in tags:
            true_tags.append(field.db_name)

    if "guid" in tags:
        true_tags.append("guid")

    tom_label_modified = tom_label.replace("{{ax_form_name}}", form_name)
    tom_label_modified = tom_label_modified.replace(
        "{{ax_db_name}}", form_db_name)

    texts = re.split('{{.*?}}', tom_label_modified)
    true_texts = []
    for text in texts:
        if text != "":
            true_texts.append("'" + text + "'")
        else:
            true_texts.append(text)

    if not true_tags:
        return f"{true_texts[0]}"

    zip_result = zip(true_texts, true_tags)
    tom_view_arr = [x for item in zip_result for x in item]
    tom_view_arr_clean = [name for name in tom_view_arr if name != ""]

    sql_tom_name = " || ".join(tom_view_arr_clean)
    return sql_tom_name


class SqliteDialect(object):
    """SQL query for Sqlite database"""
    name = 'sqlite'
    version = None

    def get_type(self, type_name) -> str:
        """Get dialect specific type"""
        sqlite_types = {
            'TEXT': 'TEXT',
            'VARCHAR(255)': 'TEXT',
            'INT': 'INTEGER',
            'DECIMAL(65,2)': 'REAL',
            'BOOL': 'NUMERIC',
            'GUID': 'TEXT',
            'JSON': 'TEXT',
            'TIMESTAMP': 'INTEGER',
            'BLOB': 'BLOB',
            'JSON': 'TEXT'
        }
        return sqlite_types[type_name]

    def get_value_sql(self, type_name, value=None):
        """ get string to be placed inside SQL """
        ret_val = None

        if "VARCHAR" in type_name:
            ret_val = "'" + value + "'" if value else 'NULL'
        elif "TEXT" in type_name:
            # val = re.escape(val).replace("\_", "_").replace("\%", "%")
            ret_val = "'" + value + "'" if value else 'NULL'
        elif "TIMESTAMP" in type_name:
            ret_val = "CAST('" + str(value) + \
                "' AS INTEGER)" if value else 'NULL'
        elif "DECIMAL" in type_name:
            ret_val = "CAST(" + str(value).replace(",", ".") + \
                " AS REAL)" if value else 'NULL'
        elif "INT" in type_name:
            ret_val = str(value) if value else 'NULL'
        elif "BOOL" in type_name:
            if value:
                ret_val = "1"
            else:
                ret_val = "0"
        elif "JSON" in type_name:
            new_string = json.dumps(value)
            ret_val = f"'{new_string}'"
        else:
            ret_val = "'" + value + "'" if value else 'NULL'

        return ret_val

    def select_all(
            self,
            ax_form,
            quicksearch=None,
            server_filter=None,
            guids=None):
        """ Select fields from table """
        try:
            sql_params = {}

            tom_name = this.get_tom_sql(
                form_db_name=ax_form.db_name,
                form_name=ax_form.name,
                tom_label=ax_form.tom_label,
                fields=ax_form.db_fields)

            fields_sql = ", ".join(
                field.db_name for field in ax_form.db_fields)

            quicksearch_sql = ''
            if quicksearch:
                sql_params['quicksearch'] = quicksearch
                quicksearch_sql = (
                    f"AND axLabel LIKE ('%' || :quicksearch || '%') "
                )

            serverfilter_sql = ''
            if server_filter and server_filter["params"]:
                serverfilter_sql = f"AND ({server_filter['sql']})"
                for key, param in server_filter["params"].items():
                    sql_params[key] = param

            guids_sql = ''
            if guids:
                guids_array = json.loads(guids)['items']
                guids_string = ''
                if guids_array:
                    for check_guid in guids_array:
                        try:
                            uuid.UUID(check_guid)
                        except Exception:
                            logger.exception(
                                f"Error in guids argument. Cant parse json")
                            raise

                    guids_string = ", ".join(
                        "'" + item + "'" for item in guids_array)
                guids_sql = f"OR guid IN ({guids_string})"
            sql = (
                f"SELECT guid, axState, axNum, {fields_sql}"
                f", {tom_name} as axLabel FROM {ax_form.db_name}"
                f" WHERE (1=1 {quicksearch_sql} {serverfilter_sql}) {guids_sql}"
            )

            result = ax_model.db_session.execute(
                sql,
                sql_params
            ).fetchall()

            return result
            # names = [row[0] for row in result]
        except Exception:
            logger.exception(
                f"Error executing SQL - quicksearch {ax_form.db_name}")
            raise

    def select_one(self, form_db_name, fields_list, row_guid):
        """ Select fields from table for one row """
        try:
            fields_string = 'guid, axState, axNum'
            for field_name in fields_list:
                fields_string += f", {field_name}"

            sql = (f"SELECT {fields_string} "
                   f"FROM {form_db_name} "
                   f"WHERE guid='{row_guid}'"
                   )
            result = ax_model.db_session.execute(sql).fetchall()
            return result
            # names = [row[0] for row in result]
        except Exception:
            logger.exception(f"Error executing SQL - select {form_db_name}")
            raise

    def insert(self, form, to_state_name, new_guid):
        """ Insert row into database and set state with AxForm field values"""
        try:
            fields_db_names = []

            value_strings = []
            for field in form.fields:
                if field.needs_sql_update:
                    fields_db_names.append(field.db_name)
                    value_strings.append(
                        self.get_value_sql(
                            type_name=field.field_type.value_type,
                            value=field.value
                        )
                    )

            column_sql = ", ".join(fields_db_names)
            values_sql = ", ".join(value_strings)

            striped_new_guid = str(new_guid).replace('-', '')

            sql = (
                f"INSERT INTO {form.db_name} "
                f"(guid, axState, {column_sql}) "
                f"VALUES ('{striped_new_guid}', '{to_state_name}', {values_sql});"
            )
            result = ax_model.db_session.execute(sql)

            last_guid_result = ax_model.db_session.execute(
                f"SELECT guid FROM {form.db_name} WHERE rowid={result.lastrowid}"
            ).fetchall()
            last_guid = last_guid_result[0]['guid']

            ax_model.db_session.commit()
            return last_guid
        except Exception:
            logger.exception('Error executing SQL - insert')
            raise

    def update(self, form, to_state_name, row_guid):
        """ Update database row based of AxForm fields values"""
        try:
            value_strings = []
            for field in form.fields:
                if field.needs_sql_update:
                    current_value = self.get_value_sql(
                        type_name=field.field_type.value_type,
                        value=field.value
                    )
                    value_strings.append(f"{field.db_name}={current_value}")

            values_sql = ", ".join(value_strings)
            sql = (
                f"UPDATE {form.db_name} "
                f"SET axState='{to_state_name}', {values_sql} "
                f"WHERE guid='{row_guid}' "
            )
            result = ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
            return result
        except Exception:
            logger.exception('Error executing SQL - update')
            raise

    def delete(self, form, row_guid):
        """ Update database row based of AxForm fields values"""
        try:
            sql = (
                f"DELETE FROM {form.db_name} WHERE guid='{row_guid}' "
            )
            ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
        except Exception:
            logger.exception('Error executing SQL - delete')
            raise

    def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid VARCHAR PRIMARY KEY,
                axNum INTEGER NOT NULL,
                axState VARCHAR NOT NULL
            );"""
            ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'ALTER TABLE {old} RENAME TO {new};'
            ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise

    def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE {db_name};'
            ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise

    def add_column(self, table: str, db_name: str, type_name: str) -> None:
        """Add column"""
        try:
            dialect_type = self.get_type(type_name=type_name)
            sql = f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"
            ax_model.db_session.execute(sql)
            ax_model.db_session.commit()
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Sqlite allows rename of column only from version 3.25.0.
        We have to reacreate table and copy data"""
        try:
            del type_name
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == table
            ).first()

            create_tmp = (
                f"CREATE TABLE _ax_tmp ("
                f"guid VARCHAR, "
                f"axNum INTEGER, "
                f"axState VARCHAR"
            )
            for field in ax_form.db_fields:
                db_name = field.db_name if field.db_name != old_name else new_name
                db_type = self.get_type(field.field_type.value_type)
                create_tmp += f", {db_name}  {db_type}"

            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid, axNum, axState'
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
                raise

            ax_model.db_session.commit()
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

            create_tmp = (
                f"CREATE TABLE _ax_tmp ("
                f"guid VARCHAR, "
                f"axNum INTEGER, "
                f"axState VARCHAR"
            )
            for field in ax_form.db_fields:
                db_type = self.get_type(field.field_type.value_type)
                if field.db_name != column:
                    create_tmp += f", {field.db_name}  {db_type}"
            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid, axNum, axState'
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
                raise

            ax_model.db_session.commit()
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
                axNum INTEGER NOT NULL,
                axState VARCHAR NOT NULL
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
                axNum INT NOT NULL,
                axState VARCHAR(255) NOT NULL
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
