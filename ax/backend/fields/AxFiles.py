"""Fields functions - before, after / insert, update, delete
"""
import os
import shutil
import backend.misc as ax_misc


def after_update(field, before_form, tobe_form, action, current_user):
    """
    Moves uploaded files from /uploads/tmp/<file_guid>/<file_name> folder to
    /uploads/form_files/<form_guid>/<row_guid>/<file_guid>/<file_name>

    WARNING! do not use ax_model.db_session.commit() here!

    Returns:
        Object: Returns updated value of current field"""
    del before_form, action, current_user

    uploads_path = ax_misc.path('uploads')
    tmp_folder = os.path.join(uploads_path, 'tmp')
    row_folder = os.path.join(uploads_path, 'form_files', str(
        tobe_form.guid), str(tobe_form.row_guid))
    value_guids = []

    if field.value:
        for file in field.value:
            value_guids.append(file['guid'])
            source_folder = os.path.join(uploads_path, 'tmp', file['guid'])
            tmp_path = os.path.join(tmp_folder, file['guid'], file['name'])
            dist_folder = os.path.join(row_folder, file['guid'])
            dist_path = os.path.join(row_folder, file['guid'], file['name'])

            # if file exists in tmp - move it to row folder
            if os.path.lexists(tmp_path) is True:
                if os.path.exists(dist_folder) is False:
                    os.makedirs(dist_folder)
                shutil.move(tmp_path, dist_path)
                shutil.rmtree(source_folder)

    if os.path.exists(row_folder) is True:
        # if row directory contains sub dirs with guid wich is not
        # in current value -> then file was deleted from field data,
        # We must delete this file from filesystem
        for root, dirs, _ in os.walk(row_folder):
            del root
            for dir_name in dirs:
                if dir_name not in value_guids:
                    dir_to_delete = os.path.join(row_folder, dir_name)
                    shutil.rmtree(dir_to_delete)

    return field.value


def after_insert(field, before_form, tobe_form, action, current_user):
    """ Do the same as after_update """
    return after_update(field, before_form, tobe_form, action, current_user)


def after_delete(field, before_form, tobe_form, action, current_user):
    """
    Deletes all files uploaded for current row

    WARNING! do not use ax_model.db_session.commit() here!

    Returns:
        Object: Returns updated value of current field"""
    del before_form, action, current_user

    uploads_path = ax_misc.path('uploads')
    row_folder = os.path.join(uploads_path, 'form_files', str(
        tobe_form.guid), str(tobe_form.row_guid))

    if os.path.exists(row_folder) is True:
        shutil.rmtree(row_folder)

    return field.value
