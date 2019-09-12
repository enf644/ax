
import os
import sys
from loguru import logger
from dotmap import DotMap

import backend.dialects as ax_dialects

this = sys.modules[__name__]


async def aexec(code, localz, **kwargs):
    """ This function wraps python code from AxAction with async function
    and runs it """
    # Restore globals later
    args = ", ".join(list(kwargs.keys()))
    code_from_action = code.replace("\n", "\n    ")
    async_code = (f"async def func({args}):"
                  f"\n    {code_from_action}"
                  f"\n    return ax")
    exec(async_code, {}, localz)    # pylint: disable=exec-used
    # Don't expect it to return from the coro.
    result = await localz["func"](**kwargs)
    return result


async def execute_field_code(code, form, arguments=None):
    """ Used to execute AxField backend code. see /backend/fields for info """
    localz = dict()
    ax = DotMap()  # javascript style dicts item['guid'] == item.guid
    ax.row.guid = form.row_guid
    ax.form = form
    ax.sql = ax_dialects.dialect.custom_query
    for field in form.db_fields:
        ax.row[field.db_name] = field.value
    if arguments:
        for key, value in arguments.items():
            ax[key] = value
    localz['ax'] = ax

    try:
        await aexec(code=str(code), localz=localz, ax=ax)
        ret_ax = localz['ax']
        return ret_ax
    except SyntaxError as err:
        return err
    except Exception as err:    # pylint: disable=broad-except
        return err
