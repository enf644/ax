"""AxNum field type functions - before, after / insert, update, delete"""
import sys
import traceback
import ujson as json
from backend.model import AxMetric


async def before_insert(db_session, field, before_form, tobe_form, action,
                        current_user):
    """
    Executes python code from AxField.private_options

    Returns:
        Object: Returns updated value of current field"""
    del before_form, action, current_user, tobe_form

    if not field.private_options_json or field.private_options_json == '{}':
        return None

    # get current counter from AxMetric for current key
    # if there is none -> create one

    options = json.loads(field.private_options_json)
    code = options['algorithm']
    key = options['counterKey']

    if not key:
        return None

    current_counter = db_session.query(AxMetric).filter(
        AxMetric.key == key
    ).first()

    current_value = None
    if current_counter:
        current_value = current_counter.value
    else:
        current_counter = AxMetric()
        current_counter.key = key
        current_counter.value = None
        db_session.add(current_counter)

    localz = dict()
    localz['ax_counter'] = current_value
    localz['ax_num'] = current_value

    try:
        exec(code, globals(), localz)  # pylint: disable=W0122
        current_counter.value = localz['ax_counter']
        field.needs_sql_update = True
        field.value = localz['ax_num']
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
        ret_data = {
            "exception": {
                "error_class": error_class,
                "line_number": line_number,
                "detail": detail
            },
        }
        field.value = json.dumps(ret_data)
    except Exception as err:  # pylint: disable=W0703
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        del cl, exc
        line_number = traceback.extract_tb(tb)[-1][1]
        del tb
        ret_data = {
            "exception": {
                "error_class": error_class,
                "line_number": line_number,
                "action_name": action.name,
                "detail": detail
            }
        }
        field.value = json.dumps(ret_data)

    return field.value

man = """
SELECT *
FROM "Wine" WHERE 'asd' 
"""
