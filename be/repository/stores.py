import inspect
import datetime
import cPickle

import shared.roles
import bases.persistence as persistence
import pg_schemas
import pgdb

from commonlib.helpers import odict

PGStore = persistence.PGStore

def selfless_locals(data):
    data.pop('self')
    return data

class UserStore(PGStore):
    model = pg_schemas.User
    def add(self, username, password, enabled):
        data = selfless_locals(locals())
        return self._add(**data)

class ContactStore(PGStore):
    model = pg_schemas.Contact
    def add(self, owner, email, address, city, country, pincode, homephone, mobile, fax, skype, sip):
        data = selfless_locals(locals())
        return self._add(**data)

class MemberPrefStore(PGStore):
    model = pg_schemas.MemberPref
    def add(self, member, language="en", theme="default"):
        data = selfless_locals(locals())
        return self._add(**data)

class MemberStore(PGStore):
    model = pg_schemas.Member
    def add(self, id, contact_id, created):
        self._add(id=id, contact=contact_id, created=created)
        return id


class MemberProfileStore(PGStore):
    model = pg_schemas.MemberProfile
    def add(self, member, first_name, last_name, display_name, short_description, long_description, website, twitter, facebook, blog, linkedin, use_gravtar):
        data = selfless_locals(locals())
        return self._add(**data)

class RegisteredStore(PGStore):
    model = pg_schemas.Registered
    def add(self, activation_key, first_name, last_name, email, ipaddr):
        data = selfless_locals(locals())
        return self._add(**data)

class SessionStore(PGStore):
    model = pg_schemas.Session
    def add(self, token, user_id):
        data = selfless_locals(locals())
        data['created'] = datetime.datetime.now()
        return self._add(**data)

class BizProfileStore(PGStore):
    model = pg_schemas.BizProfile
    def add(self, short_description, long_description, tags, website, twitter, facebook, linkedin, blog):
        data = selfless_locals(locals())
        return self._add(**data)

class BizplaceProfileStore(PGStore):
    model = pg_schemas.BizplaceProfile
    def add(self, short_description, long_description, tags, website, twitter, facebook, linkedin, blog):
        data = selfless_locals(locals())
        return self._add(**data)

class BizStore(PGStore):
    model = pg_schemas.Biz
    def add(self, name, created, contact=None, enabled=True):
        data = dict(name=name, created=created, contact=contact, enabled=enabled)
        return self._add(**data)

class BizplaceStore(PGStore):
    model = pg_schemas.BizPlace
    def add(self, name, enabled, created, langs, tz, holidays, biz):
        data = selfless_locals(locals())
        return self._add(**data)

class RoleStore(PGStore):
    model = pg_schemas.Role

    def load(self):
        role_names_persisted = [r.name for r in role_store.get_all(['name'])]
        perms_persisted = permission_store.get_all(['name', 'id'])
        perm_names_persisted = [p.name for p in perms_persisted]
        perm_name_id_map = dict((p.name, p.id) for p in perms_persisted)

        for role in shared.roles.all_roles:
            if role.name not in role_names_persisted:
                permission_ids = [perm_name_id_map[p.name] for p in role.permissions]
                role_store.add(role.name, role.label, role.description, permission_ids)

    def add(self, name, label, description, permissions):
        data = selfless_locals(locals())
        return self._add(**data)

class PermissionStore(PGStore):
    model = pg_schemas.Permission
    def add(self, name, label, description):
        data = selfless_locals(locals())
        return self._add(**data)

    def load(self):
        perms_persisted = permission_store.get_all(['name', 'id'])
        perm_names_persisted = [p.name for p in perms_persisted]
        perm_name_id_map = dict((p.name, p.id) for p in perms_persisted)

        for perm in shared.roles.all_permissions:
            if perm.name not in perm_names_persisted:
                p_id = permission_store.add(perm.name, perm.label, perm.description)
                perm_name_id_map[perm.name] = p_id

class UserRoles(PGStore):
    model = pg_schemas.UserRole
    def make_contexted_roles(self, context, roles):
        if context:
            role_ids = [(context + '::' + str(r.id)) for r in roles]
        else:
            role_ids = [str(r.id) for r in roles]
        return role_ids

    def add(self, user, context, roles):
        new_roles = self.make_contexted_roles(context, roles)
        current_roles = [ur.role_id for ur in self.get_by(user_id=user.id, _fields=['role_id'])]
        print new_roles, current_roles
        roles_to_add = set(new_roles).difference(current_roles)
        for role in roles_to_add:
            self._add(user_id=user.id, role_id=role)

class UserPermissions(PGStore):
    model = pg_schemas.UserPermission
    def make_contexted_perms(self, context, permission_ids):
        if context:
            permission_ids = [(context + '::' + str(p)) for p in permission_ids]
        else:
            permission_ids = [str(p.id) for p in permissions]
        return permission_ids

    def add(self, user, context, permission_ids):
        new_permissions = self.make_contexted_perms(context, permission_ids)
        current_permissions = [up.permission_id for up in self.get_by(user_id=user.id, _fields=['permission_id'])]
        perms_to_add = set(new_permissions).difference(current_permissions)
        for perm in perms_to_add:
            self._add(user_id=user.id, permission_id=perm)

class req_odicter(odict):
    def __init__(self, *args, **kw):
        super(req_odicter, self).__init__(*args, **kw)
        #import ipdb
        #ipdb.set_trace()
        self['req_data'] = cPickle.loads(str(self._req_data))

class RequestStore(PGStore):
    model = pg_schemas.Request
    odicter = req_odicter

    def add(self, requestor_id, name, created, status, approver_perm, req_data):
        return self._add(name=name, requestor_id=requestor_id, created=created, approver_perm=approver_perm, status=status, \
            _req_data=cPickle.dumps(req_data))

class PlanStore(PGStore):
    model = pg_schemas.Plan
    def add(self, name, bizplace_id, description, enabled, created):
        data = selfless_locals(locals())
        return self._add(**data)

class PlanSubscribersStore(PGStore):
    model = pg_schemas.PlanSubscribers
    def add(self, plan_id, subscriber_id):
        data = selfless_locals(locals())
        return self._add(**data)

#class ActivityStore(PGStore):
#    model = pg_schemas.Activity
#
#    def add(self, name, added):
#        return self._add(name=name,added=added)

userstore = UserStore()
contactstore = ContactStore()
memberstore = MemberStore()
profilestore = MemberProfileStore()
registered_store = RegisteredStore()
session_store = SessionStore()
permission_store = PermissionStore()
role_store = RoleStore()
user_perms_store = UserPermissions()
user_roles_store = UserRoles()
biz_store = BizStore()
bizplace_store = BizplaceStore()
bizprofile_store = BizProfileStore()
bizplaceprofile_store = BizplaceProfileStore()
request_store = RequestStore()
plan_store = PlanStore()
plansubscribers_store = PlanSubscribersStore()
#activity_store = ActivityStore
memberpref_store = MemberPrefStore()

def find_models(schemas):
    models = []
    for name in dir(pg_schemas):
        o = getattr(pg_schemas, name)
        if inspect.isclass(o) and issubclass(o, pg_schemas.Model) and not o is pg_schemas.Model:
            models.append(o)
    return models

def startup():
    global role_store, permission_store
    models = find_models(pg_schemas)
    for model in models:
        print "setting up: ", model.__name__
        model.load_schema(env.context.db)
    permission_store.load()
    permission_store = persistence.CachedStore(permission_store)
    role_store.load()
    role_store = persistence.CachedStore(role_store)

def destroy_all():
    models = find_models(pg_schemas)
    for model in models:
        print "Destroying: ", model.table_name
        q = 'DROP TABLE ' + model.table_name
        env.context.db.execute(q)
