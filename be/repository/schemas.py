import cPickle

import redis
import redisco
import redisco.models as models

class User(models.Model):
    username = models.Attribute(required=True, unique=True)
    password = models.Attribute()
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    last_seen = models.DateTimeField()

class Contact(models.Model):
    address = models.Attribute(indexed=False, default=None)
    city = models.Attribute(indexed=False, default=None)
    country = models.Attribute(indexed=False, default=None)
    pincode = models.Attribute(indexed=False, default=None)
    organization = models.Attribute(default=None)
    home_no = models.Attribute(indexed=False, default=None)
    mobile_no = models.Attribute(indexed=False, default=None)
    fax_no = models.Attribute(indexed=False, default=None)
    email = models.Attribute(required=True)
    skype_name = models.Attribute(indexed=False, default=None)
    sip_id = models.Attribute(indexed=False, default=None)

class MemberPref(models.Model):
    theme = models.Attribute(default="default")
    language = models.Attribute(default="en")

class MemberServices(models.Model):
    webpage = models.BooleanField(default=False)

class MemberProfileSecurity(models.Model):
    membership_id = models.IntegerField(required=True)
    property_name = models.Attribute(required=True)
    #level = models.ListField(required=True) # 0 off 1 on: [anonymous access][all locations][same location][private]

class Profile(models.Model):
    first_name = models.Attribute(required=True)
    last_name = models.Attribute(default='')
    display_name = models.Attribute()
    short_description = models.Attribute(indexed=False)
    long_description = models.Attribute(indexed=False)
    interests = models.ListField(str, default=[])
    expertise = models.Attribute()
    website = models.Attribute(indexed=False, default=None)
    twitter = models.ListField(str, indexed=False)
    facebook = models.ListField(str, indexed=False)
    blog = models.ListField(str, indexed=True)
    linkedin = models.ListField(str, indexed=True)
    use_gravtar = models.BooleanField(default=True)

# Container objects
class Member(models.Model):
    user = models.ReferenceField(User, default=None)
    pref = models.ReferenceField(MemberPref, default=None)
    profile = models.ReferenceField(Profile, default=None)
    services = models.ReferenceField(MemberServices, default=None)
    contact = models.ReferenceField(Contact, default=None)

class Business(models.Model):
    profile = models.ReferenceField(Profile, default=None)
    contact = models.ReferenceField(Contact, default=None)

class Registered(models.Model):
    activation_key = models.Attribute(required=True)
    first_name = models.Attribute(required=True)
    last_name = models.Attribute(default='')
    email = models.Attribute(required=True)
    ipaddr = models.Attribute(default='')

class Session(models.Model):
    token = models.Attribute(required=True)
    user_id = models.Attribute(required=True)
    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField()

class Permission(models.Model):
    name = models.Attribute(required=True)
    label = models.Attribute(required=True)
    description = models.Attribute(default='')

class Role(models.Model):
    name = models.Attribute(required=True)
    label = models.Attribute(required=True)
    description = models.Attribute(default='')
    permissions = models.ListField(Permission, required=True)

class UserRoles(models.Model):
    user_id = models.Attribute(required=True)
    role_ids = models.ListField(str, default=[], required=True)

class UserPermissions(models.Model):
    user_id = models.Attribute(required=True)
    permission_ids = models.ListField(str, default=[], required=True)

class BizProfile(models.Model):
    name = models.Attribute(required=True)
    short_description = models.Attribute(indexed=False)
    long_description = models.Attribute(indexed=False)
    twitter_handle = models.Attribute(indexed=False)
    facebook_page = models.Attribute(indexed=False)
    blog = models.Attribute(indexed=True)
    linkedin_biz = models.Attribute(indexed=True)
    tags = models.ListField(str, default=[])

class BizInvoicingPref(models.Model):
    invoice_logo = models.Attribute()

class Biz(models.Model):
    name = models.Attribute(required=True)
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    city = models.Attribute()
    langs = models.ListField(str, default=['en'])
    timezone = models.Attribute()
    holidays = models.ListField(str, default=['6'])
    logo = models.Attribute()
    profile = models.ReferenceField(Profile, default=None)
    services = models.ReferenceField(MemberServices, default=None)
    contact = models.ReferenceField(Contact, default=None)
    booking_contact = models.Attribute()

class Request(models.Model):
    name = models.Attribute(required=True)
    created = models.DateTimeField(auto_now_add=True)
    acted_at = models.DateTimeField()
    requestor_id = models.Attribute(required=True)
    status = models.IntegerField(default=0)
    approver_id = models.Attribute()
    request_note = models.Attribute()
    _req_data = models.Attribute()
    def _get_req_data(self):
        return cPickle.loads(self._req_data)
    def _set_req_data(self, data):
        self._req_data = cPickle.dumps(data, -1)
    req_data = property(_get_req_data, _set_req_data)

class Plan(models.Model):
    name = models.Attribute(required=True)
    description = models.Attribute(indexed=False)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.Attribute(required=True)
    subscribers = models.ListField(int, default=[])
