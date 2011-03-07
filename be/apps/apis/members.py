from pycerberus.schema import SchemaValidator
import pycerberus.validators as v

import be.bases.constants as constants
import be.repository.stores as stores

import commonlib.messaging.email as emaillib
import commonlib.messaging as messaging

memberstore = stores.memberstore

def create_activation_key():
    return "12345"

def register(first_name, last_name, email, ipaddr):
    activation_key = create_activation_key()
    registered = stores.registered_store.add(activation_key, first_name, last_name, email, ipaddr)
    activation_url = "http://127.0.0.1/activate/" + activation_key
    data = dict (first_name = first_name, activation_url = activation_url)
    mail_data = messaging.activation.create_message(data)
    return env.mailer.send(**mail_data)

register.exec_mode = constants.exec_modes.BG

def get_activation_info(activation_key):
    member = registered_store.fetch_one(activation_key=activation_key)
    if not member:
        raise erros.APIExcecutionError("Invalid/Expired Activation key")
    return registered_store.obj2dict(member)

def activate(activation_key, **member_data):
    registered = get_activation_info(activation_key)
    member_data.update(registered_store.obj2dict(registered))
    member = add(**member_data)
    return member.id

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
        details[attr] = memberstore.obj2dict(getattr(member, attr))
    return details

def get_attribute(member_id, attrbute):
    return 1
