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
        profile.save()
        member = self.model(user=user, contact=contact, profile=profile)
        member.save()
        return member

class ProfileStore(RedisStore):
    model = schemas.Profile
    def add(self, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar):
        profile = self.model(first_name=first_name, last_name=last_name, short_description=short_description, long_description=long_description, twitter_handle=twitter_handle, facebook_name=facebook_name, blog=blog, linkedin_contact=linkedin_contact, use_gravtar=use_gravtar)
        return profile

userstore = UserStore()
contactstore = ContactStore()
memberstore = MemberStore()
profilestore = ProfileStore()
