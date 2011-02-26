from pycerberus.schema import SchemaValidator
import pycerberus.validators as v

import be.repository.stores as stores
memberstore = stores.memberstore

class AddValidator(SchemaValidator):
    username = v.StringValidator(required=True)
    password = v.StringValidator(required=True)
    enabled = v.EmailAddressValidator(required=True)

def add(username, password, enabled, email, address=None, city=None, country=None, pincode=None, organization=None, home_no=None, mobile_no=None, fax_no=None, skype_name=None, sip_id=None, website=None, first_name=None, last_name=None, short_description=None, long_description=None, twitter_handle=None, facebook_name=None, blog=None, linkedin_contact=None, use_gravtar=None):
    member = memberstore.add(username, password, enabled, email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar)
    return member.id
add.validator = AddValidator()

def get(member_id):
    return memberstore.fetch_by_id(member_id)

def get_details(member_id, **data):
    member = memberstore.fetch_by_id(member_id)
    details = {}
    for attr in ('user', 'contact', 'profile'):
        details[attr] = getattr(member, attr).attributes_dict
    return details

def get_attribute(member_id, attrbute):
    return 1
