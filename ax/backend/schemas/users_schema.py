"""Defines Users Scheme and all mutations"""

# import asyncio
import uuid
import graphene
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from passlib.hash import pbkdf2_sha256
# from loguru import logger

from backend.misc import convert_column_to_string
from backend.model import AxUser, GUID, AxGroup2Users, AxRole2Users
import backend.model as ax_model
import backend.cache as ax_cache
import backend.dialects as ax_dialects
# import backend.pubsub as ax_pubsub
from backend.schemas.types import User
from backend.auth import ax_admin_only

convert_sqlalchemy_type.register(GUID)(convert_column_to_string)


class CreateUser(graphene.Mutation):
    """ Creates AxUser """
    class Arguments:  # pylint: disable=missing-docstring
        email = graphene.String()
        name = graphene.String()
        short_name = graphene.String()
        password = graphene.String()
        avatar_tmp = graphene.String()
        info = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)
    msg = graphene.String()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        # avatar_tmp = args.get('avatar_tmp')

        err = 'Error in gql mutation - users_schema -> CreateUser.'
        with ax_model.try_catch(info.context['session'], err) as db_session:

            ax_user = db_session.query(AxUser).filter(
                AxUser.email == args.get('email')
            ).first()
            if ax_user:
                return CreateUser(user=None, ok=False, msg="users.email-exists")

            new_user = AxUser()
            new_user.email = args.get('email')
            new_user.name = args.get('name')
            new_user.short_name = args.get('short_name')
            new_user.info = args.get('info')
            new_user.password = pbkdf2_sha256.hash(args.get('password'))
            db_session.add(new_user)
            db_session.flush()

            return CreateUser(user=new_user, ok=True, msg=None)


class UpdateUser(graphene.Mutation):
    """ Update AxUser """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        short_name = graphene.String()
        info = graphene.String()
        password = graphene.String(required=False, default_value=None)
        avatar_tmp = graphene.String(required=False, default_value=None)

    ok = graphene.Boolean()
    user = graphene.Field(User)

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        # avatar_tmp = args.get('avatar_tmp')
        guid = args.get('guid')

        err = 'Error in gql mutation - users_schema -> UpdateUser.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            ax_user = db_session.query(AxUser).filter(
                AxUser.guid == uuid.UUID(guid)
            ).first()

            if args.get('name'):
                ax_user.name = args.get('name')
            if args.get('short_name'):
                ax_user.short_name = args.get('short_name')
            if args.get('info'):
                ax_user.info = args.get('info')
            if args.get('password'):
                ax_user.password = pbkdf2_sha256.hash(args.get('password'))

            db_session.flush()
            return UpdateUser(user=ax_user, ok=True)


class DeleteUser(graphene.Mutation):
    """ Deletes AxField witch is tab """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - form_schema -> DeleteUser.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            guid = args.get('guid')
            ax_user = db_session.query(AxUser).filter(
                AxUser.guid == uuid.UUID(guid)
            ).first()
            db_session.delete(ax_user)
            return DeleteUser(deleted=guid, ok=True)


class CreateGroup(graphene.Mutation):
    """ Creates AxUser with is_group=True """
    class Arguments:  # pylint: disable=missing-docstring
        short_name = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)
    msg = graphene.String()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> CreateGroup.'
        with ax_model.try_catch(info.context['session'], err) as db_session:

            ax_user = db_session.query(AxUser).filter(
                AxUser.short_name == args.get('short_name')
            ).filter(
                AxUser.is_group.is_(True)
            ).first()

            if ax_user:
                return CreateGroup(
                    user=None, ok=False, msg="users.group-name-exists")

            new_user = AxUser()
            new_user.short_name = args.get('short_name')
            new_user.is_group = True
            db_session.add(new_user)
            db_session.flush()

            return CreateGroup(user=new_user, ok=True, msg=None)


class UpdateGroup(graphene.Mutation):
    """ Creates AxUser with is_group=True """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        short_name = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)
    msg = graphene.String()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> UpdateGroup.'
        with ax_model.try_catch(info.context['session'], err) as db_session:

            existing_user = db_session.query(AxUser).filter(
                AxUser.short_name == args.get('short_name')
            ).filter(
                AxUser.is_group.is_(True)
            ).first()

            if existing_user:
                return UpdateGroup(
                    user=None, ok=False, msg="users.group-name-exists")

            ax_user = db_session.query(AxUser).filter(
                AxUser.guid == uuid.UUID(args.get('guid'))
            ).filter(
                AxUser.is_group.is_(True)
            ).first()

            ax_user.short_name = args.get('short_name')
            db_session.flush()

            return UpdateGroup(user=ax_user, ok=True, msg=None)


class AddUserToGroup(graphene.Mutation):
    """ Creates AxGroup2Users """
    class Arguments:  # pylint: disable=missing-docstring
        user_guid = graphene.String()
        group_guid = graphene.String()

    ok = graphene.Boolean()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> AddUserToGroup.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            user_guid = uuid.UUID(args.get('user_guid'))
            group_guid = uuid.UUID(args.get('group_guid'))

            group2user = db_session.query(AxGroup2Users).filter(
                AxGroup2Users.user_guid == user_guid
            ).filter(
                AxGroup2Users.group_guid == group_guid
            ).first()
            if group2user:
                return AddUserToGroup(ok=True)

            group2user = AxGroup2Users()
            group2user.group_guid = group_guid
            group2user.user_guid = user_guid
            db_session.add(group2user)
            db_session.flush()

            return AddUserToGroup(ok=True)


class RemoveUserFromGroup(graphene.Mutation):
    """ Deletes AxGroup2Users """
    class Arguments:  # pylint: disable=missing-docstring
        user_guid = graphene.String()
        group_guid = graphene.String()

    ok = graphene.Boolean()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> RemoveUserFromGroup.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            user_guid = uuid.UUID(args.get('user_guid'))
            group_guid = uuid.UUID(args.get('group_guid'))

            db_session.query(AxGroup2Users).filter(
                AxGroup2Users.user_guid == user_guid
            ).filter(
                AxGroup2Users.group_guid == group_guid
            ).delete()
            db_session.flush()

            return RemoveUserFromGroup(ok=True)


class AddUserToRole(graphene.Mutation):
    """ Creates AxRole2Users """
    class Arguments:  # pylint: disable=missing-docstring
        user_guid = graphene.String()
        role_guid = graphene.String()

    ok = graphene.Boolean()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> AddUserToRole.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            user_guid = uuid.UUID(args.get('user_guid'))
            role_guid = uuid.UUID(args.get('role_guid'))

            role2user = db_session.query(AxRole2Users).filter(
                AxRole2Users.user_guid == user_guid
            ).filter(
                AxRole2Users.role_guid == role_guid
            ).first()
            if role2user:
                return AddUserToRole(ok=True)

            role2user = AxRole2Users()
            role2user.role_guid = role_guid
            role2user.user_guid = user_guid
            db_session.add(role2user)
            db_session.flush()

            return AddUserToRole(ok=True)


class RemoveUserFromRole(graphene.Mutation):
    """ Removes AxRole2Users """
    class Arguments:  # pylint: disable=missing-docstring
        user_guid = graphene.String()
        role_guid = graphene.String()

    ok = graphene.Boolean()

    @ax_admin_only
    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        err = 'Error in gql mutation - users_schema -> RemoveUserFromRole.'
        with ax_model.try_catch(info.context['session'], err) as db_session:
            user_guid = uuid.UUID(args.get('user_guid'))
            role_guid = uuid.UUID(args.get('role_guid'))

            db_session.query(AxRole2Users).filter(
                AxRole2Users.user_guid == user_guid
            ).filter(
                AxRole2Users.role_guid == role_guid
            ).delete()
            db_session.flush()

            return RemoveUserFromRole(ok=True)


class LogoutUser(graphene.Mutation):
    """ Delete refresh jwt token from cache """
    # class Arguments:  # pylint: disable=missing-docstring
    #     user_guid = graphene.String()
    #     role_guid = graphene.String()

    ok = graphene.Boolean()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        """ Delete refresh token from cache """
        current_user = info.context['user']
        user_guid = current_user.get('user_id', None) if current_user else None
        if user_guid:
            key = f'refresh_token_{user_guid}'
            await ax_cache.cache.delete(key)

        return LogoutUser(ok=True)


class UsersQuery(graphene.ObjectType):
    """AxUser queryes"""
    all_users = graphene.List(
        User,
        search_string=graphene.Argument(type=graphene.String, required=False),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    all_groups = graphene.List(
        User,
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    group_users = graphene.List(
        User,
        group_guid=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    role_users = graphene.List(
        User,
        role_guid=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    page_users = graphene.List(
        User,
        page_guid=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    users_and_groups = graphene.List(
        User,
        search_string=graphene.Argument(type=graphene.String, required=False),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    find_user = graphene.Field(
        User,
        guid=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )
    current_ax_user = graphene.Field(
        User,
        update_time=graphene.Argument(type=graphene.String, required=False)
    )

    @ax_admin_only
    async def resolve_all_users(
            self, info, search_string=None, update_time=None):
        """Get all users"""
        del update_time
        err = 'Error in GQL query - all_users.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            query = User.get_query(info)  # SQLAlchemy query
            users_list = []
            if not search_string:
                users_list = query.filter(AxUser.is_group.is_(False)).all()
            else:
                users_list = query.filter(
                    AxUser.is_group.is_(False)
                ).filter(
                    AxUser.short_name.ilike(f"%{search_string}%")
                ).all()
            return users_list

    @ax_admin_only
    async def resolve_all_groups(self, info, update_time=None):
        """Get all groups"""
        del update_time
        err = 'Error in GQL query - resolve_all_groups.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            query = User.get_query(info)  # SQLAlchemy query
            users_list = query.filter(
                AxUser.is_group.is_(True)
            ).filter(
                AxUser.is_all_users.is_(False)
            ).filter(
                AxUser.is_everyone.is_(False)
            ).all()
            return users_list

    @ax_admin_only
    async def resolve_group_users(self, info, group_guid, update_time=None):
        """Get users of group"""
        del update_time
        err = 'Error in GQL query - resolve_all_groups.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            user_list = await ax_dialects.dialect.select_group_users(
                db_session=info.context['session'], group_guid=group_guid)
            user_guids = []
            for user in user_list:
                user_guids.append(user['guid'])
            query = User.get_query(info)  # SQLAlchemy query
            ret_list = query.filter(AxUser.guid.in_(user_guids)).all()
            return ret_list

    @ax_admin_only
    async def resolve_role_users(self, info, role_guid, update_time=None):
        """Get users of role"""
        del update_time
        err = 'Error in GQL query - resolve_role_users.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            user_list = await ax_dialects.dialect.select_role_users(
                db_session=info.context['session'], role_guid=role_guid)
            user_guids = []
            for user in user_list:
                user_guids.append(user['guid'])
            query = User.get_query(info)  # SQLAlchemy query
            ret_list = query.filter(AxUser.guid.in_(user_guids)).all()
            return ret_list

    @ax_admin_only
    async def resolve_page_users(self, info, page_guid, update_time=None):
        """Get users that allowed to view page"""
        del update_time
        err = 'Error in GQL query - resolve_page_users.'
        with ax_model.try_catch(
                info.context['session'], err, no_commit=True):
            user_list = await ax_dialects.dialect.select_page_users(
                db_session=info.context['session'], page_guid=page_guid)
            user_guids = []
            for user in user_list:
                user_guids.append(user['guid'])
            query = User.get_query(info)  # SQLAlchemy query
            ret_list = query.filter(AxUser.guid.in_(user_guids)).all()
            return ret_list

    async def resolve_users_and_groups(
            self, info, search_string=None, update_time=None):
        """Get all users and groups in one search"""
        del update_time
        err = 'Error in GQL query - users_and_groups.'
        with ax_model.try_catch(info.context['session'], err, no_commit=True):
            query = User.get_query(info)
            users_list = []
            if not search_string:
                users_list = query.all()
            else:
                users_list = query.filter(
                    AxUser.short_name.ilike(f"%{search_string}%")
                ).all()
            return users_list

    def resolve_find_user(self, info, guid, update_time):
        """default find method"""
        del update_time
        err = 'Error in GQL query - find_user.'
        with ax_model.try_catch(info.context['session'], err, no_commit=True):
            query = User.get_query(info)
            ax_user = query.filter(AxUser.guid == guid).first()
            return ax_user

    def resolve_current_ax_user(self, info, update_time):
        """ Returns current AxUser """
        del update_time
        err = 'Error in GQL query - find_user.'
        with ax_model.try_catch(info.context['session'], err, no_commit=True):
            if not info.context['user']:
                return None

            user_guid = info.context['user']['user_id']
            query = User.get_query(info)
            ax_user = query.filter(AxUser.guid == uuid.UUID(user_guid)).first()
            return ax_user


class UsersSubscription(graphene.ObjectType):
    """GraphQL subscriptions"""


class UsersMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    add_user_to_group = AddUserToGroup.Field()
    remove_user_from_group = RemoveUserFromGroup.Field()
    add_user_to_role = AddUserToRole.Field()
    remove_user_from_role = RemoveUserFromRole.Field()
    logout_user = LogoutUser.Field()
