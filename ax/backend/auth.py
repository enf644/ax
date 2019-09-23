import sys
import functools
from sanic_jwt import exceptions, initialize, Configuration
from sanic_jwt.decorators import _do_protection

import backend.cache as ax_cache

this = sys.modules[__name__]
users = None
useremail_table = None
userguid_table = None


class User:
    def __init__(self, guid, email, password, short_name):
        self.user_id = guid
        self.email = email
        self.password = password
        self.short_name = short_name

    def __repr__(self):
        return "User(guid='{}')".format(self.user_id)

    def to_dict(self):
        return {"user_id": self.user_id, "short_name": self.short_name}


async def authenticate(request, *args, **kwargs):
    """ - """
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if not email or not password:
        raise exceptions.AuthenticationFailed("Missing email or password.")
    user = this.useremail_table.get(email, None)
    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")
    if password != user.password:
        raise exceptions.AuthenticationFailed("Password is incorrect.")
    return user


def ax_protected(initialized_on=None, **kw):
    """ Wrapper for @protected sanic_jwt decorator. 
    If not authorisation token is present - then it is anon user, do not send
    401 error  """
    def _aux(view):
        @functools.wraps(view)
        async def _inner(request, *args, **kwargs):
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


async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        user = this.userguid_table.get(user_id, None)
        user = {
            "user_id": user_id,
            "is_admin": False,
            "short_name": user.short_name
        }
        return user
    else:
        return None


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    key = f'refresh_token_{user_id}'
    await ax_cache.cache.set(key, refresh_token)


async def retrieve_refresh_token(request, user_id, *args, **kwargs):
    key = f'refresh_token_{user_id}'
    return await ax_cache.cache.get(key)


class AxConfiguration(Configuration):
    url_prefix = '/api/auth'


def init_auth(sanic_app):
    this.users = [User('uber-guid', "enf644@gmail.com", "123", "enfik"),
                  User('uber-guid', "admin@ax.ru", "123", "admin")]

    this.useremail_table = {u.email: u for u in this.users}
    this.userguid_table = {u.user_id: u for u in this.users}

    initialize(sanic_app,
               authenticate=authenticate,
               configuration_class=AxConfiguration,
               refresh_token_enabled=True,
               store_refresh_token=store_refresh_token,
               retrieve_refresh_token=retrieve_refresh_token,
               retrieve_user=retrieve_user,
               expiration_delta=60)
