import datetime

import bases.persistence as persistence
import schemas

RedisStore = persistence.RedisStore

class UserStore(RedisStore):
    model = schemas.User
    def connect(self):
        pass
    def add(self, username, password, enabled):
        user = self.model(username=username, password=password, enabled=enabled)
        if not user.is_valid():
            print user.errors # fail here
        else:
            user.save()
            return user

class ContactStore(RedisStore):
    model = schemas.Contact
    def add(self, email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website):
        contact = self.model(email=email, address=address, city=city, country=country, pincode=pincode, organization=organization, home_no=home_no, mobile_no=mobile_no, fax_no=fax_no, skype_name=skype_name, sip_id=skype_name, website=website)
        contact.save()
        return contact

class MemberPrefStore(RedisStore):
    model = schemas.MemberPref
    def add(self, language="en", theme="default"):
        pref = self.model(language=language, theme=theme)
        pref.save()
        return pref

class MemberStore(RedisStore):
    model = schemas.Member
    def add(self, username, password, enabled, email, language, display_name, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar):
        user = userstore.add(username, password, enabled)
        contact = contactstore.add(email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website)
        profile = profilestore.add(first_name, last_name, display_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar)
        pref = memberpref_store.add(language=language)
        member = self.model(id=user.id, user=user, contact=contact, profile=profile, pref=pref)
        member.save()
        return member
    def edit(self, member_id, mod_data):
        stores = dict(profile=profilestore,
            contact = contactstore,
            user = userstore)
        member = self.fetch_by_id(member_id)
        for k, v in mod_data.items():
            oid = getattr(member, k+'_id')
            store = stores[k]
            store.edit(oid, v)

    @classmethod
    def obj2dict(cls, obj):
        d = {}
        for attr in ('user', 'contact', 'profile'):
            d[attr] = RedisStore.obj2dict(getattr(obj, attr))
        return d

class ProfileStore(RedisStore):
    model = schemas.Profile
    def add(self, first_name, last_name, display_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar):
        profile = self.model(first_name=first_name, last_name=last_name, display_name=display_name, short_description=short_description, long_description=long_description, twitter_handle=twitter_handle, facebook_name=facebook_name, blog=blog, linkedin_contact=linkedin_contact, use_gravtar=use_gravtar)
        if not profile.is_valid():
            print profile.errors # fail here
        profile.save()
        return profile

class RegisteredStore(RedisStore):
    model = schemas.Registered
    def add(self, activation_key, first_name, last_name, email, ipaddr):
        registered = self.model(activation_key=activation_key, first_name=first_name, last_name=last_name, email=email, ipaddr=ipaddr)
        if not registered.is_valid():
            print registered.errors # fail here
        else:
            registered.save()
            return registered

class SessionStore(RedisStore):
    model = schemas.Session
    def add(self, token, user_id):
        session = self.model(token=token, user_id=user_id)
        session.save()
        return session

class BizProfileStore(RedisStore):
    model = schemas.BizProfile
    def add(self, short_description, long_description, tags, website, twitter, facebook, linkedin, blog):
        self.model(short_description=short_description, long_description=long_description, tags=tags, twitter=twitter, facebook=facebook, linkedin=linkedin, website=website, blog=blog)
        biz_profile = self.model(short_description=short_description, long_description=long_description, tags=tags, twitter=twitter, facebook=facebook, linkedin=linkedin, website=website, blog=blog)
        if not biz_profile.is_valid():
            print biz_profile.errors # fail here
        else:
            biz_profile.save()
            return biz_profile

class BizStore(RedisStore):
    model = schemas.Biz
    def add(self, name, city, short_description, long_description, tags, website, twitter, facebook, linkedin, blog, enabled):
        biz_profile = bizprofile_store.add(short_description=short_description, long_description=long_description, tags=tags, twitter=twitter, facebook=facebook, linkedin=linkedin, website=website, blog=blog)
        biz = self.model(name=name, city=city, enabled=enabled, profile=biz_profile)
        if not biz.is_valid():
            print biz.errors
        biz.save()
        return biz

class RoleStore(RedisStore):
    model = schemas.Role
    def add(self, name, label, description, permissions):
        role = self.model(name=name, label=label, description=description, permissions=permissions)
        role.save()
        return role

class PermissionStore(RedisStore):
    model = schemas.Permission
    def add(self, name, label, description):
        perm = self.model(name=name, label=label, description=description)
        perm.save()
        return perm

class UserRoles(RedisStore):
    model = schemas.UserRoles
    def make_contexted_roles(self, context, roles):
        if context:
            ctx_ref = self.ref(context)
            role_ids = [(ctx_ref + '::' + str(p.id)) for p in roles]
        else:
            role_ids = [p.id for p in roles]
        return role_ids

    def add(self, user, context, roles):
        ctx_roles = self.make_contexted_roles(context, roles)
        user_roles  = self.model(user_id=user.id, role_ids=ctx_roles)
        user_roles.save()
        return user_roles

    def extend(self, user, context, roles):
        ctx_roles = self.make_contexted_roles(context, roles)
        user_roles = self.fetch_one_by(user_id=user.id)
        current_role_ids = user_roles.role_ids
        ctx_roles = [r for r in ctx_roles if r not in current_role_ids]
        user_roles.role_ids.extend(ctx_roles)
        user_roles.save()

class UserPermissions(RedisStore):
    model = schemas.UserPermissions
    def make_contexted_perms(self, context, permissions):
        if context:
            ctx_ref = self.ref(context)
            permission_ids = [(ctx_ref + '::' + str(p.id)) for p in permissions]
        else:
            permission_ids = [p.id for p in permissions]
        return permission_ids

    def add(self, user, context, permissions):
        ctx_permissions = self.make_contexted_perms(context, permissions)
        user_perms = self.model(user_id=user.id, permission_ids=ctx_permissions)
        user_perms.save()
        return user_perms

    def extend(self, user, context, permissions):
        ctx_permissions = self.make_contexted_perms(context, permissions)
        user_perms = self.fetch_one_by(user_id=user.id)
        current_perm_ids = user_perms.permission_ids
        ctx_permissions = [r for r in ctx_permissions if r not in current_perm_ids]
        user_perms.permission_ids.extend(ctx_permissions)
        user_perms.save()

class RequestStore(RedisStore):
    model = schemas.Request
    def add(self, requestor_id, name, status, approver_perm, req_data):
        req = self.model(name=name, requestor_id=requestor_id, approver_perm=approver_perm, status=status)
        if not req.is_valid(): print req.errors # fail here
        req.req_data = req_data
        req.save()
        return req
    @classmethod
    def obj2dict(cls, obj):
        d = RedisStore.obj2dict(obj)
        d.pop('_req_data')
        d['req_data'] = obj.req_data
        return d

class PlanStore(RedisStore):
    model = schemas.Plan
    def add(self, name, description, biz_id):
        plan = self.model(name=name, description=description, biz_id=biz_id)
        if not plan.is_valid(): print plan.errors # fail here
        plan.save()
        return plan

class ActivityStore(RedisStore):
    model = schemas.Activity
    #defs = definitions.Activity

    def add(self, name, added):
        activity = self.model(name=name,added=added)
	if not activity.is_valid():
            print "Errors adding", activity.errors
	else:
            activity.save()
            return activity

userstore = UserStore()
contactstore = ContactStore()
memberstore = MemberStore()
profilestore = ProfileStore()
registered_store = RegisteredStore()
session_store = SessionStore()
role_store = persistence.CachedStore(RoleStore())
permission_store = persistence.CachedStore(PermissionStore())
user_perms_store = UserPermissions()
user_roles_store = UserRoles()
biz_store = BizStore()
bizprofile_store = BizProfileStore()
request_store = RequestStore()
plan_store = PlanStore()
activity_store = ActivityStore
memberpref_store = MemberPrefStore()
