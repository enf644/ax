""" Auth module based on sanic-jwt """

import sys
import uuid
import functools
from loguru import logger
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_
from sanic_jwt import exceptions, initialize, Configuration
from sanic_jwt.decorators import _do_protection

from backend.model import AxUser, AxGroup2Users, AxRole2Users, \
    AxRoleFieldPermission, AxForm
import backend.cache as ax_cache
import backend.model as ax_model
import backend.misc as ax_misc

this = sys.modules[__name__]
users = None


async def get_allowed_fields_dict(ax_form, user_guid, state_guid):
    """ Gets allowed fields for user -> dict['field_guid'] = 1/2 """
    cache_keys = []
    field_guids = []
    allowed_fields_dict = {}
    for field in ax_form.fields:
        user_guid = str(user_guid)
        field_guid = str(field.guid)
        state_guid = str(state_guid)
        key = f"perm_{user_guid}_{field_guid}_{state_guid}"
        cache_keys.append(key)
        field_guids.append(str(field.guid))

    cache_results = await ax_cache.cache.multi_get(cache_keys)

    for idx, field_guid in enumerate(field_guids):
        perm_value = cache_results[idx]
        allowed_fields_dict[field_guid] = perm_value

    return allowed_fields_dict


async def check_if_admin(user_guid, db_session):
    """ Checks if user is adimn and writes  <user_is_admin_{user_guid}> cache"""
    err = "Error -> Auth -> check_if_admin"
    with ax_model.try_catch(db_session, err):
        # Get admin group, check if
        admin_group = db_session.query(AxUser).filter(
            AxUser.is_admin.is_(True)
        ).filter(
            AxUser.is_group.is_(True)
        ).first()

        group2user = db_session.query(AxGroup2Users).filter(
            AxGroup2Users.group_guid == admin_group.guid
        ).filter(
            AxGroup2Users.user_guid == uuid.UUID(user_guid)
        ).first()

        if group2user:
            key = f'user_is_admin_{user_guid}'
            await ax_cache.cache.set(key, True)


async def write_perm_cache(db_session, user_guid):
    """ On each user token refresh we write to cache permissions for
        each field/state combination """
    user_and_groups = []
    user_and_groups.append(uuid.UUID(user_guid))

    # Get everyone and all_users groups
    everyone_all_groups = db_session.query(AxUser).filter(
        or_(AxUser.is_all_users.is_(True), AxUser.is_everyone.is_(True))
    ).all()
    for grp in everyone_all_groups:
        if grp.guid not in user_and_groups:
            user_and_groups.append(grp.guid)

    # Get user groups
    group2user_result = db_session.query(AxGroup2Users).filter(
        AxGroup2Users.user_guid == uuid.UUID(user_guid)
    ).all()
    for g2u in group2user_result:
        if g2u.group_guid not in user_and_groups:
            user_and_groups.append(g2u.group_guid)

    # Get roles of user and his groups
    roles_guids = []
    role2user_result = db_session.query(AxRole2Users).filter(
        AxRole2Users.user_guid.in_(user_and_groups)
    ).all()
    for r2u in role2user_result:
        if r2u.role_guid not in roles_guids:
            roles_guids.append(r2u.role_guid)

    # Get AxRoleFieldPermission for those roles
    forms_guids = []
    perms = db_session.query(AxRoleFieldPermission).filter(
        AxRoleFieldPermission.role_guid.in_(roles_guids)
    ).all()
    for perm in perms:
        if perm.form_guid not in forms_guids:
            forms_guids.append(perm.form_guid)

    # Get all forms with perms
    all_forms = db_session.query(AxForm).filter(
        AxForm.guid.in_(forms_guids)
    ).all()

    perm_cache_pairs = []
    debug_list = []

    # For each form
    for ax_form in all_forms:
        # For each field
        for ax_field in ax_form.no_tab_fields:
            # For each state
            for ax_state in ax_form.perm_states:
                read = False
                edit = False
                # For each perm
                form_perms = [p for p in perms if (
                    p.form_guid == ax_form.guid and
                    p.state_guid == ax_state.guid)]
                for perm in form_perms:
                    # if perm is set to whole form
                    # if perm is set to tab
                    # if perm is set to field

                    if (perm.field_guid is None or
                            perm.field_guid == ax_field.parent or
                            perm.field_guid == ax_field.guid):

                        if perm.read is True:
                            read = True
                        if perm.edit is True:
                            edit = True

                # Write cache perm_<user_guid>_<field_guid>_<state_guid> = 0/1/2
                field_guid = str(ax_field.guid)
                state_guid = str(ax_state.guid)
                key = f"perm_{user_guid}_{field_guid}_{state_guid}"
                value = 0
                if read is True:
                    value = 1
                if edit is True:
                    value = 2

                perm_cache_pairs.append([key, value])
                debug_list.append(
                    [f"{ax_state.name} -> {ax_field.db_name} -> {value}"])

    expire_seconds = 60 * 20  # 20 mins
    await ax_cache.cache.multi_set(perm_cache_pairs, ttl=expire_seconds)


async def authenticate(request, *args, **kwargs):
    """ - """
    del args, kwargs
    msg = "Error -> Auth -> authenticate"
    with ax_model.scoped_session(msg) as db_session:
        email = request.json.get("email", None)
        password = request.json.get("password", None)

        if not email or not password:
            raise exceptions.AuthenticationFailed("Missing email or password.")

        user = db_session.query(AxUser).filter(
            AxUser.email == email
        ).first()

        if user is None:
            raise exceptions.AuthenticationFailed("User not found.")

        if not pbkdf2_sha256.verify(password, user.password):
            raise exceptions.AuthenticationFailed("Password is incorrect.")

        await check_if_admin(user_guid=str(user.guid), db_session=db_session)
        await write_perm_cache(db_session=db_session, user_guid=str(user.guid))

        # Save short_name and email in cache
        name_key = f'user_short_name_{user.guid}'
        await ax_cache.cache.set(name_key, user.short_name)
        email_key = f'user_email_{user.guid}'
        await ax_cache.cache.set(email_key, user.email)

        db_session.expunge(user)
        return user


def ax_protected(initialized_on=None, **kw):
    """ Wrapper for @protected sanic_jwt decorator.
    If not authorisation token is present - then it is anon user, do not send
    401 error  """
    def _aux(view):
        @functools.wraps(view)
        async def _inner(request, *args, **kwargs):
            # If there is no jwt headers -> then this is everyone user.
            # We must not protect route
            if 'authorization' not in request.headers:
                return await view(request, *args, **kwargs)
            if not "Bearer" in request.headers['authorization']:
                return await view(request, *args, **kwargs)

            kwargs.update({
                'initialized_on': initialized_on,
                'kw': kw,
                'request': request,
                'f': view,
            })
            return await _do_protection(*args, **kwargs)
        return _inner
    return _aux


def ax_admin_only(func):
    """ Decorator to check if user is admin """
    async def check_admin(*args, **kwargs):
        user = args[1].context["user"]
        if user and user["is_admin"] is True:
            return await func(*args, **kwargs)
        else:
            logger.error('Only for admins error')
            raise Exception('Only for admins')
    return check_admin


async def retrieve_user(request, payload, *args, **kwargs):
    """ Get user info. This info is transfered into routes with inject_user """
    del request, args, kwargs
    if payload:
        user_id = payload.get('user_id', None)

        if not ax_misc.string_is_guid(user_id):
            return None

        email = await ax_cache.cache.get(f'user_email_{user_id}')

        if not email:
            msg = "Auth -> retrieve_user"
            with ax_model.scoped_session(msg) as db_session:
                await check_if_admin(user_guid=user_id, db_session=db_session)
                await write_perm_cache(db_session=db_session, user_guid=user_id)
                email = await ax_cache.cache.get(f'user_email_{user_id}')

        short_name = await ax_cache.cache.get(f'user_short_name_{user_id}')
        is_admin = await ax_cache.cache.get(f'user_is_admin_{user_id}')

        user = {
            "user_id": str(user_id),
            "is_admin": is_admin,
            "short_name": short_name,
            "email": email
        }
        return user
    else:
        return None


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    """ Store refresh token in cache and write all perms cache for user """
    del args, kwargs
    key = f'refresh_token_{user_id}'
    await ax_cache.cache.set(key, refresh_token)


async def retrieve_refresh_token(request, user_id, *args, **kwargs):
    """ Get refresh token from cache and refresh all perms cache for user """
    del request, args, kwargs
    key = f'refresh_token_{user_id}'
    refresh_token = await ax_cache.cache.get(key)

    if refresh_token:
        with ax_model.scoped_session("Auth.store_refresh_token") as db_session:
            await check_if_admin(user_guid=user_id, db_session=db_session)
            await write_perm_cache(db_session=db_session, user_guid=user_id)

    return refresh_token


class AxConfiguration(Configuration):
    """ sanic-jwt config class """
    url_prefix = '/api/auth'


def init_auth(sanic_app):
    """ Initiate sanic-jwt module """

    initialize(sanic_app,
               authenticate=authenticate,
               configuration_class=AxConfiguration,
               refresh_token_enabled=True,
               store_refresh_token=store_refresh_token,
               retrieve_refresh_token=retrieve_refresh_token,
               retrieve_user=retrieve_user,
               expiration_delta=60)
