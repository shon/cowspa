import datetime

import commonlib.helpers
import be.bases as bases
import schemas

class RedisStore(bases.BaseStore):
    def add(self, **data):
        """
        returns oid
        """
        raise NotImplemented

    def edit(self, oid, mod_data):
        """
        """

    def list(self, limit=None, order_by=None):
        """
        """
        raise NotImplemented

    def fetch_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)

    def fetch_one_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)[0]

    def fetch_by_id(self, oid):
        """
        """
        return self.model.objects.get_by_id(oid)

    def remove(self, oid):
        obj = self.model.objects.filter(id=oid)[0]
        return obj.delete()

    @classmethod
    def obj2dict(self, obj):
        d = {}
        for k, v in obj.attributes_dict.items():
            if isinstance(v, datetime.datetime):
                v = v.isoformat()
            d[k] = v
        return d


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
        return contact


class MemberStore(RedisStore):
    model = schemas.Member
    def add(self, username, password, enabled, email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar):
        user = userstore.add(username, password, enabled)
        contact = contactstore.add(email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website)
        profile = profilestore.add(first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar)
        user.save()
        contact.save()
        member = self.model(user=user, contact=contact, profile=profile)
        member.save()
        return member

class ProfileStore(RedisStore):
    model = schemas.Profile
    def add(self, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar):
        profile = self.model(first_name=first_name, last_name=last_name, short_description=short_description, long_description=long_description, twitter_handle=twitter_handle, facebook_name=facebook_name, blog=blog, linkedin_contact=linkedin_contact, use_gravtar=use_gravtar)
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

class BizStore(RedisStore):
    model = schemas.Biz
    def add(self, name):
        biz = self.model(name=name)
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
    def add(self, user, context, roles):
        ctx_ref = self.ref(context)
        ctx_roles = [(ctx_ref + '::' + str(r.id)) for r in roles]
        user_roles  = self.model(user_id=user.id, role_ids=ctx_roles)
        user_roles.save()
        return user_roles

class UserPermissions(RedisStore):
    model = schemas.UserPermissions
    def add(self, user, context, permissions):
        ctx_ref = self.ref(context)
        ctx_permissions = [(ctx_ref + '::' + str(p.id)) for p in permissions]
        user_perms = self.model(user_id=user.id, permission_ids=ctx_permissions)
        user_perms.save()
        return user_perms

userstore = UserStore()
contactstore = ContactStore()
memberstore = MemberStore()
profilestore = ProfileStore()
registered_store = RegisteredStore()
session_store = SessionStore()
role_store = bases.CachedStore(RoleStore())
permission_store = bases.CachedStore(PermissionStore())
user_perms_store = UserPermissions()
user_roles_store = UserRoles()
biz_store = BizStore()
