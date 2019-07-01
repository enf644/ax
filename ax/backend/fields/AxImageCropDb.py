"""Fields functions - before, after / insert, update, delete
"""
import os
import uuid
import shutil
import backend.misc as ax_misc


def before_update(field, before_form, tobe_form, action, current_user):
    """
    Reads file from /uploads/tmp/<file_guid>/<file_name> and sets it as
    field value. It will be inserted to database
    WARNING! do not use ax_model.db_session.commit() here!
    Returns:
        Object: Returns updated value of current field"""
    del before_form, action, current_user
    file = field.value

    # value contaiins tmp file dict
    if file and 'guid' in file:
        tmp_folder = ax_misc.path(f"uploads/tmp/{file['guid']}")
        tmp_path = os.path.join(tmp_folder, file['name'])
        with open(tmp_path, 'rb') as img:
            field.value = img.read()
        shutil.rmtree(tmp_folder)
    else:
        field.needs_sql_update = False

    return field.value


def before_insert(field, before_form, tobe_form, action, current_user):
    """ Do the same as after_update """
    return before_update(field, before_form, tobe_form, action, current_user)
