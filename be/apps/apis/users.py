import itertools

from pycerberus.schema import SchemaValidator
from pycerberus.validators import StringValidator

import commonlib
import be.bases.errors as errors
import be.repository.stores as stores

userstore = stores.userstore
biz_store = stores.biz_store
session_store = stores.session_store
role_store = stores.role_store
user_perms_store = stores.user_perms_store
user_roles_store = stores.user_roles_store

role_names_ordered = ['activated', 'member', 'host', 'director', 'network', 'admin']

def create_session(username):
    token  = commonlib.helpers.random_key_gen()
    user = userstore.fetch_one_by(username=username)
    session = session_store.add(token, user.id)
    return session.token

def get_or_create_session(username):
    user = userstore.fetch_one_by(username=username)
    try:
        session = session_store.fetch_one_by(user_id=user.id)
        token = session.token
    except IndexError:
        token = create_session(username)
    return token

def authenticate(username, password):
    try:
        user = userstore.fetch_one_by(username=username)
    except IndexError:
        return False
    return user.password == password

def login(username, password):
    if authenticate(username, password):
        return get_or_create_session(username)
    raise errors.WrapperException(errors.auth_failed, '')

class AddValidator(SchemaValidator):
    username = StringValidator(required=True)
    password = StringValidator(required=True)

def add(username, password, enabled=True):
    user = userstore.add(username, password, enabled)
    return user.id

def assign_roles(user_id, biz_id, role_names):
    if isinstance(role_names, basestring):
        role_names = [role_names]
    # to ensure user and biz exist
    user = userstore.fetch_by_id(user_id)
    biz = biz_store.fetch_by_id(biz_id)
    roles = [role_store.fetch_one_by(name=name) for name in role_names]
    role_ids = list(r.id for r in roles)
    user_roles = user_roles_store.soft_fetch_one_by(user_id=user_id)
    if not user_roles:
        user_roles_store.add(user, biz, roles)
    else:
        user_roles.role_ids.extend(role_ids)
        user_perms.save()

    user_perms = user_perms_store.soft_fetch_one_by(user_id=user_id)

    permissions = list(itertools.chain(*[role.permissions for role in roles]))

    if user_perms:
        user_perms.permission_ids.extend(p.id for p in permissions)
        user_perms.save()
    else:
        user_perms = user_perms_store.add(user, biz, permissions)

    return user_perms.permission_ids

def get_context_permissions(context, user):
    perms = user_perms_store.fetch_one_by(user_id=user_id)
    ctx_ref = context.ref()
    return (p for p in perms if p.startswith(ctx_ref))

def strip_context_from_ref(ref):
    return ref.split('::')[-1]

def info(username):
    user = userstore.fetch_one_by(username=username)
    return dict(role=get_biggest_role(user.id))

def get_biggest_role(user_id):
    role_ids = user_roles_store.fetch_one_by(user_id=user_id).role_ids
    if role_ids:
        role_names = tuple(role_store.fetch_by_id(strip_context_from_ref(rid)).name for rid in role_ids)
        return [name for name in role_names_ordered if name in role_names][-1]
    return role_names[0]
