"""
All SQL queries are generated throw this module.
sea init_dialects
"""
import sys
import sqlite3
import uuid
import re
from loguru import logger
from sqlalchemy.exc import DatabaseError
import ujson as json
import backend.model as ax_model
from backend.model import AxForm
import backend.misc as ax_misc

this = sys.modules[__name__]
dialect_name = None
dialect = None


class PorstgreDialect(object):
    """SQL query for Postgre SQL database"""

    name = 'postgre'
    version = None


    async def get_tom_sql(self, form_db_name, form_name, tom_label, fields):
        """    '{{name}} {{surname}}' -> 'Mikhail Marenov'
        Each form have 1toM label option. It could be '{{name}} {{surname}}'
        This function custructs SELECT statement string that will return
        'Mikhail Marenov' string as result. Where 'Mikhail' is from 'name'
        column and 'Marenov' from 'surname' column

        Args:
            form_db_name (str): db_name of form. Same as table name.
            form_name (str): Name of form. Used to replace {{ax_form_name}}
            tom_label (str): Tom label option of AxForm
            fields (List(AxField)): List of all AxFields of current form

        Returns:
            str: SQL statement to be placed in SELECT statement
        """
        tags = re.findall("{{(.*?)}}", tom_label)
        true_tags = []
        for field in fields:
            if field.db_name in tags:
                true_tags.append('"' + field.db_name + '"')

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


    async def get_type(self, type_name):
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
            'BLOB': 'bytea'
        }
        return postgre_types[type_name]

    async def get_select_sql(self, type_name, db_name):
        """Some value types need a transformation inside SQL Select statement.

        Args:
            type_name (str): value of AxField.AxFieldType.value_type, like INT
            db_name (str): AxField.db_name, the column name of table

        Returns:
            str: SQL statement to be placed in select section
                SET <db_name>=<this function>
        """
        ret_val = None
        if "BLOB" in type_name:
            ret_val = f"octet_length({db_name}) as {db_name}"
        else:
            ret_val = db_name
        return ret_val


    async def get_value_sql(self, type_name, db_name):
        """Some value types need a cast inside SQL.
        Like [UPDATE <table> SET <field>=<this function>]
        It uses param names same as db_name, like :surname

        Args:
            type_name (str): value of AxFieldType.value_type, like INT
            db_name (str): AxField.db_name, the column name of table

        Returns:
            str: SQL statement to be placed in value section
                SET <db_name>=<this function>
        """
        del type_name
        ret_val = None
        # if "TIMESTAMP" in type_name:
        #     ret_val = f"CAST(:{db_name} AS INTEGER)"
        # elif "DECIMAL" in type_name:
        #     ret_val = f"CAST(:{db_name} AS REAL)"
        # else:
        ret_val = f":{db_name}"
        return ret_val


    async def get_value_param(self, type_name, value=None):
        """ Some value types needs to convert field value before submiting
        to SQL.

        Args:
            type_name (str): value of AxFieldType.value_type, like INT
            value (object, optional): Value of field. Defaults to None.

        Returns:
            object: initial value of converted value if needed by field type
        """
        ret_param = None
        if "DECIMAL" in type_name:
            ret_param = str(value).replace(",", ".") if value else None
        elif "JSON" in type_name:
            ret_param = json.dumps(value) if value else None
        else:
            ret_param = value if value else None
        return ret_param


    def custom_query(self, sql, variables=None):
        """ Executes any SQL. Used in action python code.
        This method is SYNC, leave it so

        Args:
            sql (str): Any sql that needs to be executed

        Returns:
            List(Dict(column_name: value)): result of SQL query
        """
        try:
            res = None
            try:
                if variables:
                    res = ax_model.db_session.execute(sql, variables)
                else:
                    res = ax_model.db_session.execute(sql)
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise

            if res and res.returns_rows:
                return res.fetchall()
            return res
        except Exception:
            logger.exception(
                f"Error executing SQL - {sql}")
            raise



    async def select_all(self, ax_form, quicksearch=None, server_filter=None,
                         guids=None):
        """ Select * from table

        Args:
            ax_form (AxForm): Current AxForm
            quicksearch (str, optional): Search string from AxGrid.vue
            server_filter (Dict, optional): Dicts with current grid server-
            filter. Constructed by query builder javascript plugin:
                sql (str): Sql expression with params, like 'price > :price'
                params (str): Sql params of query. lile {'price': 20000}
            guids (str, optional): JSON containing list of guids, that must be
                selected. Used in 1tom fields. Where you need to display only
                selected guids.

        Returns:
            List(Dict): Result of SqlAlchemy query. List of rows
        """
        try:
            sql_params = {}

            tom_name = await self.get_tom_sql(
                form_db_name=ax_form.db_name,
                form_name=ax_form.name,
                tom_label=ax_form.tom_label,
                fields=ax_form.db_fields)

            fields_sql = ", ".join(
                '"' + field.db_name + '"' for field in ax_form.db_fields)

            quicksearch_sql = ''
            if quicksearch:
                sql_params['quicksearch'] = quicksearch
                quicksearch_sql = (
                    f"AND \"axLabel\" LIKE ('%' || :quicksearch || '%') "
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
                    for idx, guid in enumerate(guids_array):
                        del guid
                        guids_array[idx] = guids_array[idx].replace('-', '')

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
                if not quicksearch_sql and not serverfilter_sql:
                    guids_sql = f"AND guid IN ({guids_string})"
            sql = (
                f'SELECT guid, "axState", {fields_sql}'
                f', {tom_name} as "axLabel" FROM "{ax_form.db_name}"'
                f' WHERE (1=1 {quicksearch_sql} {serverfilter_sql}) {guids_sql}'
            )
            try:
                result = ax_model.db_session.execute(
                    sql,
                    sql_params
                ).fetchall()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise

            return result
            # names = [row[0] for row in result]
        except Exception:
            logger.exception(
                f"Error executing SQL - quicksearch {ax_form.db_name}")
            raise



    async def select_one(self, form, fields_list, row_guid):
        """Select fields from table for one row

        Args:
            form (AxForm): Current form
            fields_list (List(AxField)): Fields that must be selected.
            row_guid (str): String of row guid
            num_fields (List(AxField)): AxNum fields. If not empy, row will
                be searched by guid and every AxNum

        Returns:
            List(Dict(column_name: value)): result of SQL query
        """
        try:
            form_db_name = form.db_name
            num_fields = []
            for field in form.db_fields:
                if field.field_type.tag == 'AxNum':
                    num_fields.append(field)
            fields_string = 'guid, "axState"'
            for field in fields_list:
                field_name = await self.get_select_sql(
                    field.field_type.value_type, field.db_name)
                fields_string += f", {field_name}"

            sql = (f'SELECT {fields_string} '
                   f'FROM "{form_db_name}" '
                   f'WHERE guid=:row_guid')
            if num_fields:
                for num_field in num_fields:
                    sql += f" OR {num_field.db_name}=:row_guid"
            guid_or_num = str(row_guid)
            if ax_misc.string_is_guid(guid_or_num):
                guid_or_num = guid_or_num.replace('-', '')
            query_params = {"row_guid": guid_or_num}
            result = None
            try:
                result = ax_model.db_session.execute(
                    sql, query_params).fetchall()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise

            return result
            # names = [row[0] for row in result]
        except Exception:
            logger.exception(f"Error executing SQL - select_one {form_db_name}")
            raise



    async def select_field(self, form_db_name, field_db_name, row_guid):
        """Gets value of single field from SQL. Used in file viewer.
        See routes.py

        Args:
            form_db_name (str): AxForm.db_name - table name of current form
            fields_db_name (str): Db name of field
            row_guid (str): String of row guid

        Returns:
            List(Dict(column_name: value)): result of SQL query
        """
        try:
            row_guid_stripped = row_guid.replace('-', '')
            ret_value = None
            sql = (f"SELECT \"{field_db_name}\" "
                   f"FROM {form_db_name} "
                   f"WHERE guid='{row_guid_stripped}'"
                   )
            result = None
            try:
                result = ax_model.db_session.execute(sql).fetchall()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise

            if result:
                ret_value = result[0][field_db_name]
            return ret_value
        except Exception:
            logger.exception(
                f"Error executing SQL - select_field {form_db_name}")
            raise


    async def insert(self, form, to_state_name, new_guid):
        """ Insert row into database and set state with AxForm field values

        Args:
            form (AxForm): Current form with filled field values.
            to_state_name (str): Name of form state that must be set
            new_guid (str): Guid that must be used to create record.

        Returns:
            str: Guid of created row
        """
        try:
            fields_db_names = []
            query_params = {
                "ax_state": to_state_name,
                "row_guid": str(new_guid).replace('-', ''),
            }

            value_strings = []
            for field in form.fields:
                if field.needs_sql_update:
                    fields_db_names.append(f'"field.db_name"')
                    value_str = await self.get_value_sql(
                        type_name=field.field_type.value_type,
                        db_name=field.db_name)
                    value_strings.append(value_str)
                    query_params[field.db_name] = await self.get_value_param(
                        type_name=field.field_type.value_type,
                        value=field.value)

            column_sql = ", ".join(fields_db_names)
            values_sql = ", ".join(value_strings)

            sql = (
                f"INSERT INTO {form.db_name} "
                f"(guid, \"axState\", {column_sql}) "
                f"VALUES (:row_guid, :ax_state, {values_sql});"
            )
            try:
                ax_model.db_session.execute(sql, query_params)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
            return new_guid
        except Exception:
            logger.exception('Error executing SQL - insert')
            raise



    async def update(self, form, to_state_name, row_guid):
        """Update database row based of AxForm fields values

        Args:
            form (AxForm): Current form with filled field values.
            to_state_name (str): Name of form state that must be set
            row_guid (str): Guid of updated row

        Returns:
            SqlAlchemy result: Contains nothing. Not used.
        """
        try:
            value_strings = []
            query_params = {
                "ax_state": to_state_name,
                "row_guid": row_guid
            }
            for field in form.fields:
                if field.needs_sql_update:
                    current_valu_str = await self.get_value_sql(
                        type_name=field.field_type.value_type,
                        db_name=field.db_name
                    )
                    value_strings.append(
                        f"\"{field.db_name}\"={current_valu_str}")
                    query_params[field.db_name] = await self.get_value_param(
                        type_name=field.field_type.value_type,
                        value=field.value
                    )

            values_sql = ", ".join(value_strings)
            sql = (
                f"UPDATE \"{form.db_name}\" "
                f"SET \"axState\"=:ax_state, {values_sql} "
                f"WHERE guid=:row_guid "
            )
            result = None
            try:
                result = ax_model.db_session.execute(sql, query_params)
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise

            ax_model.db_session.commit()
            return result
        except Exception:
            logger.exception('Error executing SQL - update')
            raise


    async def delete(self, form, row_guid):
        """ Delete row of table of form"""
        try:
            sql = (
                f"DELETE FROM \"{form.db_name}\" WHERE guid='{row_guid}' "
            )
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - delete')
            raise


    async def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE \"{db_name}\" (
                guid UUID PRIMARY KEY,
                \"axState\" VARCHAR NOT NULL
            );"""
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    async def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'ALTER TABLE "{old}" RENAME TO "{new}";'
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise


    async def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE "{db_name}";'
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise


    async def add_column(self, table: str, db_name: str, type_name: str):
        """Add column"""
        try:
            dialect_type = await self.get_type(type_name=type_name)
            sql = f'ALTER TABLE "{table}" ADD COLUMN "{db_name}" {dialect_type}'
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    async def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Rename column"""
        try:
            del type_name
            sql = (
                f'ALTER TABLE "{table}"',
                f' RENAME COLUMN "{old_name}" TO "{new_name}";'
            )
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - rename_column')
            raise

    async def drop_column(self, table, column) -> None:
        """ Drop column """
        try:
            sql = f'ALTER TABLE "{table}" DROP COLUMN "{column}";'
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - drop_column')
            raise


class SqliteDialect(PorstgreDialect):
    """SQL query for Sqlite database"""
    name = 'sqlite'
    version = None

    async def get_type(self, type_name) -> str:
        """Get dialect specific type"""
        sqlite_types = {
            'TEXT': 'TEXT',
            'VARCHAR(255)': 'TEXT',
            'INT': 'INTEGER',
            'DECIMAL(65,2)': 'REAL',
            'BOOL': 'NUMERIC',
            'GUID': 'TEXT',
            'TIMESTAMP': 'INTEGER',
            'BLOB': 'BLOB',
            'JSON': 'TEXT'
        }
        return sqlite_types[type_name]

    async def get_select_sql(self, type_name, db_name):
        """Some value types need a transformation inside SQL Select statement.

        Args:
            type_name (str): value of AxField.AxFieldType.value_type, like INT
            db_name (str): AxField.db_name, the column name of table

        Returns:
            str: SQL statement to be placed in select section
                SET <db_name>=<this function>
        """
        ret_val = None
        if "BLOB" in type_name:
            ret_val = f"LENGTH({db_name}) as \"{db_name}\""
        else:
            ret_val = f'"db_name"'
        return ret_val

    async def get_value_sql(self, type_name, db_name):
        """Some value types need a cast inside SQL.
        Like [UPDATE <table> SET <field>=<this function>]
        It uses param names same as db_name, like :surname

        Args:
            type_name (str): value of AxFieldType.value_type, like INT
            db_name (str): AxField.db_name, the column name of table

        Returns:
            str: SQL statement to be placed in value section
                SET <db_name>=<this function>
        """
        ret_val = None
        if "TIMESTAMP" in type_name:
            ret_val = f"CAST(:{db_name} AS INTEGER)"
        elif "DECIMAL" in type_name:
            ret_val = f"CAST(:{db_name} AS REAL)"
        else:
            ret_val = f":{db_name}"
        return ret_val

    async def get_value_param(self, type_name, value=None):
        """ Some value types needs to convert field value before submiting
        to SQL.

        Args:
            type_name (str): value of AxFieldType.value_type, like INT
            value (object, optional): Value of field. Defaults to None.

        Returns:
            object: initial value of converted value if needed by field type
        """
        ret_param = None
        if "DECIMAL" in type_name:
            ret_param = str(value).replace(",", ".") if value else None
        elif "JSON" in type_name:
            ret_param = json.dumps(value) if value else None
        else:
            ret_param = value if value else None
        return ret_param


    async def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid VARCHAR PRIMARY KEY,
                axState VARCHAR NOT NULL
            );"""
            try:
                ax_model.db_session.execute(sql)
                ax_model.db_session.commit()
            except DatabaseError:
                ax_model.db_session.rollback()
                logger.exception(f"Error executing SQL, rollback! - {sql}")
                raise
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    async def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Sqlite allows rename of column only from version 3.25.0.
        We have to reacreate table and copy data"""
        try:
            del type_name
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == table
            ).first()

            drop_tmp = f"DROP TABLE IF EXISTS _ax_tmp"

            create_tmp = (
                f"CREATE TABLE _ax_tmp ("
                f"guid VARCHAR, "
                f"axState VARCHAR"
            )
            for field in ax_form.db_fields:
                db_name = field.db_name if (
                    field.db_name != old_name) else new_name
                db_type = await self.get_type(field.field_type.value_type)
                create_tmp += f", {db_name}  {db_type}"

            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid, axState'
            for field in ax_form.db_fields:
                copy_data += f", {field.db_name}"
            copy_data += f" FROM {ax_form.db_name};"

            drop_old = f"DROP TABLE {ax_form.db_name};"

            rename_tmp = f'ALTER TABLE _ax_tmp RENAME TO {ax_form.db_name};'

            try:
                ax_model.db_session.execute(drop_tmp)
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

    async def drop_column(self, table, column) -> None:
        """Sqlite does not allows to drop columns.
        We have to reacreate table and copy data"""
        try:
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.db_name == table
            ).first()

            drop_tmp = f"DROP TABLE IF EXISTS _ax_tmp"
            create_tmp = (
                f"CREATE TABLE _ax_tmp ("
                f"guid VARCHAR, "
                f"axState VARCHAR"
            )
            for field in ax_form.db_fields:
                db_type = await self.get_type(field.field_type.value_type)
                if field.db_name != column:
                    create_tmp += f", {field.db_name}  {db_type}"
            create_tmp += ');'

            copy_data = 'INSERT INTO _ax_tmp SELECT guid, axState'
            for field in ax_form.db_fields:
                if field.db_name != column:
                    copy_data += f", {field.db_name}"
            copy_data += f" FROM {ax_form.db_name};"

            drop_old = f"DROP TABLE {ax_form.db_name};"

            rename_tmp = f'ALTER TABLE _ax_tmp RENAME TO {ax_form.db_name};'

            try:
                ax_model.db_session.execute(drop_tmp)
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


class MysqlDialect(object):
    """SQL query for Mysql database"""

    name = 'mysql'
    version = None

    async def get_type(self, type_name):
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

    async def create_data_table(self, db_name: str) -> None:
        """Create table with system columns"""
        try:
            sql = f"""CREATE TABLE {db_name} (
                guid VARCHAR(64) PRIMARY KEY,
                axState VARCHAR(255) NOT NULL
            );"""
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - create_data_table')
            raise

    async def rename_table(self, old: str, new: str) -> None:
        """Rename table"""
        try:
            sql = f'RENAME TABLE `{old}` TO `{new}`'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_table')
            raise

    async def drop_table(self, db_name: str) -> None:
        """Drop table"""
        try:
            sql = f'DROP TABLE {db_name};'
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - drop_table')
            raise

    async def add_column(self, table, db_name, type_name) -> None:
        """Add column"""
        try:
            dialect_type = await self.get_type(type_name=type_name)
            sql = f"ALTER TABLE `{table}` ADD COLUMN {db_name} {dialect_type}"
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - add_column')
            raise

    async def rename_column(self, table, old_name, new_name, type_name) -> None:
        """Rename column"""
        try:
            dialect_type = await self.get_type(type_name=type_name)
            sql = (
                f"ALTER TABLE `{table}` "
                f"CHANGE COLUMN `{old_name}` `{new_name}` {dialect_type}"
            )
            ax_model.db_session.execute(sql)
        except Exception:
            logger.exception('Error executing SQL - rename_column')
            raise

    async def drop_column(self, table, column) -> None:
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
