"""AxNum field type functions - before, after / insert, update, delete"""
import ujson as json
import backend.misc as ax_misc


async def before_display(db_session, field, form, current_user):
    """
    Executes python code from AxField.private_options

    Returns:
        Object: Returns updated value of current field"""
    del current_user, db_session

    if not field.private_options_json or field.private_options_json == '{}':
        return None

    # get current counter from AxMetric for current key
    # if there is none -> create one

    options = json.loads(field.private_options_json)
    code = options['code']
    ax = await ax_misc.execute_field_code(code=code, form=form)
    field.value = ax.value
    return field.value
