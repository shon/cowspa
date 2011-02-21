import redisco
import redisco.models as models

class User(models.Model):
    username = models.Attribute(required=True, unique=True)
    password = models.Attribute()
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)

class MemberContact(models.Model):
    address = models.Attribute(indexed=False)
    pincode = models.Attribute(indexed=False)
    oranizarion = models.Attribute()
    home_no = models.Attribute(indexed=False)
    mobile_no = models.Attribute(indexed=False)
    fax_no = models.Attribute(indexed=False)
    email_address = models.Attribute(required=True, unique=True)
    skype_name = models.Attribute(indexed=False)
    sip_id = models.Attribute(indexed=False)
    website = models.Attribute(indexed=False)
    #user = models.ReferenceField(default=None)

class MemberProfile(models.Model):
    first_name = models.Attribute(required=True)
    last_name = models.Attribute(default='')
    def _get_display_name(self):
        return self.first_name + ' ' + self.last_name
    display_name = property(_get_display_name)
    description = models.Attribute(indexed=False)
    twitter_handle = models.Attribute(indexed=False)
    facebook_name = models.Attribute(indexed=False)
    blog_address = models.Attribute(indexed=True)
    linkedin_contact = models.Attribute(indexed=True)
    use_gravtar = models.BooleanField(default=True)
    #user = models.ReferenceField(default=None)
    #pref = models.ReferenceField(default=None)

class MemberPref(models.Model):
    theme = models.Attribute(default="default")
    language = models.Attribute(default="en")

class MemberServices(models.Model):
    webpage = models.BooleanField(default=False)

class MemberProfileSecurity(models.Model):
    membership_id = models.IntegerField(required=True)
    property_name = models.Attribute(required=True)
    #level = models.ListField(required=True) # 0 off 1 on: [anonymous access][all locations][same location][private]
