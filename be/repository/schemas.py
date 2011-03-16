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
    website = models.Attribute(indexed=False, default=None)

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
    def _get_display_name(self):
        return self.first_name + ' ' + self.last_name
    display_name = property(_get_display_name)
    short_description = models.Attribute(indexed=False)
    long_description = models.Attribute(indexed=False)
    twitter_handle = models.Attribute(indexed=False)
    facebook_name = models.Attribute(indexed=False)
    blog = models.Attribute(indexed=True)
    linkedin_contact = models.Attribute(indexed=True)
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
