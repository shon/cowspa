import __builtin__
import conf
import commonlib
import commonlib.helpers
import commonlib.messaging.email
import shared.roles
import be.repository.stores as stores

permission_store = stores.permission_store
role_store = stores.role_store

def init():
    class env: pass
    env.config = conf.parse_config()
    commonlib.helpers.random_key_gen = commonlib.helpers.RandomKeyFactory(env.config.random_str)
    env.mailer = commonlib.messaging.email.Mailer(env.config.mail)
    env.mailer.start()
    return env

__builtin__.env = init()

def add_roles():
    for role in shared.roles.all_roles:
        permissions = []
        for perm in role.permissions:
            permission = permission_store.soft_fetch_one_by(name=perm.name)
            if not permission:
                permission = permission_store.add(perm.name, perm.label, perm.description)
            permissions.append(permission)
        if not role_store.soft_fetch_one_by(name=role.name):
            role_store.add(role.name, role.label, role.description, permissions)

add_roles()
