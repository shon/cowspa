import __builtin__
import conf
import commonlib
import commonlib.helpers
import commonlib.messaging.email
import shared.roles
import be.repository.stores as stores
import gevent.local

def init():
    class env: pass
    env.config = conf.parse_config()
    commonlib.helpers.random_key_gen = commonlib.helpers.RandomKeyFactory(env.config.random_str)
    env.mailer = commonlib.messaging.email.Mailer(env.config.mail)
    env.mailer.start()
    env.context = gevent.local.local()
    return env

__builtin__.env = init()

def add_roles():
    for role in shared.roles.all_roles:
        permissions = []
        for perm in role.permissions:
            permission = stores.permission_store.soft_fetch_one_by(name=perm.name)
            if not permission:
                permission = stores.permission_store.add(perm.name, perm.label, perm.description)
            permissions.append(permission)
        if not stores.role_store.soft_fetch_one_by(name=role.name):
            stores.role_store.add(role.name, role.label, role.description, permissions)

add_roles()
