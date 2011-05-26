import itertools

from pycerberus.schema import SchemaValidator
from pycerberus.validators import StringValidator

import bases
import commonlib
import bases
import be.libs.signals as signals
import bases.errors as errors
import be.repository.stores as stores

userstore = stores.userstore
biz_store = stores.biz_store
session_store = stores.session_store
role_store = stores.role_store
user_perms_store = stores.user_perms_store
user_roles_store = stores.user_roles_store

role_names_ordered = ['new', 'member', 'host', 'director', 'network', 'admin']

def create_session(user_id):
    token  = commonlib.helpers.random_key_gen()
    session_store.add(token, user_id)
    return token

def get_or_create_session(username):
    user = userstore.get_one_by(username=username)
    try:
        session = session_store.get_one_by(user_id=user.id)
        token = session.token
    except IndexError:
        token = create_session(user.id)
    return token

def session_lookup(token):
    try:
        session = session_store.get_one_by(token=token)
        user_id = session.user_id
    except IndexError:
        user_id = None
    return user_id

def authenticate(username, password):
    try:
        user = userstore.get_one_by(username=username)
    except IndexError, err:
        return False
    return user.password == password

def login(username, password):
    if authenticate(username, password):
        return get_or_create_session(username)
    raise errors.WrapperException(errors.auth_failed, '')

def logout(token):
    try:
        session = session_store.get_one_by(token=token)
        session.delete()
    except Exception, err:
        print err

class AddValidator(SchemaValidator):
    username = StringValidator(required=True)
    password = StringValidator(required=True)

def add(username, password, enabled=True):
    user = userstore.add(username, password, enabled)
    return user.id

def get_user_permissions(user_id):
    return user_perms_store.get_one_by(user_id=user_id).permission_ids

def get_context_permissions(context, user):
    perms = user_perms_store.get_one_by(user_id=user_id)
    ctx_ref = context.ref()
    return (p for p in perms if p.startswith(ctx_ref))

def strip_context_from_ref(ref):
    return int(ref.split('::')[-1])

def get_biggest_role(user_id):
    role_ids = [ur.role_id for ur in user_roles_store.get_by(user_id=user_id)]
    if role_ids:
        role_names = tuple(role_store.get(strip_context_from_ref(rid)).name for rid in role_ids)
        return [name for name in role_names_ordered if name in role_names][-1]
    return role_names_ordered[0]

class Users(bases.app.Collection):
    pass

class UserMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'assign_roles']

    def info(self, username):
        user = self.store.get_one_by(username=username)
        return dict(role=get_biggest_role(user.id), id=user.id)

    def assign_roles(self, username, biz_id, role_names):
        if isinstance(role_names, basestring):
            role_names = [role_names]

        if isinstance(username, int) or (isinstance(username, basestring) and username.isdigit()):
            user = userstore.get(username)
        else:
            user = userstore.get_one_by(username=username)

        user_roles = user_roles_store.soft_get_one_by(user_id=user.id)
        roles = [role_store.get_one_by(name=name) for name in role_names]
        user_perms = user_perms_store.soft_get_one_by(user_id=user.id)
        permission_ids = list(itertools.chain(*[role.permissions for role in roles]))

        biz_ref = None
        if biz_id:
            biz_ref = biz_store.ref(biz_id)

        user_roles_store.add(user, biz_ref, roles)
        user_perms_store.add(user, biz_ref, permission_ids)

        return True

users = Users(userstore)
user_methods = UserMethods(userstore)
signals.connect("assign_roles", user_methods.assign_roles)
