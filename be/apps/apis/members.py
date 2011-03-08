import base64, random, hashlib

from pycerberus.schema import SchemaValidator
import pycerberus.validators as v

import be.bases.constants as constants
import be.repository.stores as stores

import commonlib.messaging.email as emaillib
import commonlib.messaging as messaging

memberstore = stores.memberstore
registered_store = stores.registered_store

def create_activation_key():
    return base64.b64encode(hashlib.sha256( str(random.getrandbits(256)) ).digest(), random.choice(['rA','aZ','gQ','hH','hG','aR','DD'])).rstrip('==')

def register(first_name, last_name, email, ipaddr):
    activation_key = create_activation_key()
    registered = registered_store.add(activation_key, first_name, last_name, email, ipaddr)
    activation_url = "http://127.0.0.1/members/activate/" + activation_key
    data = dict (first_name = first_name, activation_url = activation_url)
    mail_data = messaging.activation.create_message(data)
    env.mailer.send(**mail_data)
    return activation_key

register.exec_mode = constants.exec_modes.BG

def get_activation_info(activation_key):
    member = registered_store.fetch_one_by(activation_key=activation_key)
    if not member:
        raise erros.APIExcecutionError("Invalid/Expired Activation key")
    return registered_store.obj2dict(member)

def activate(activation_key, **member_data):
    activation_info = get_activation_info(activation_key)
    member_data.update(activation_info)
    member_data.pop('activation_key')
    member_data.pop('ipaddr')
    member_id = add(**member_data)
    return member_id

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
