import bases
import bases.constants as constants
import be.repository.stores as stores

import commonlib
import commonlib.messaging.email as emaillib
import commonlib.messaging as messaging

import users as userslib

memberstore = stores.memberstore
profilestore = stores.profilestore
registered_store = stores.registered_store
contactstore = stores.contactstore

create_activation_key = commonlib.helpers.random_key_gen

class Registrations(bases.app.Collection):
    def new(self, first_name, last_name, email, ipaddr, sendmail=False):
        activation_key = create_activation_key()
        registered = registered_store.add(activation_key, first_name, last_name, email, ipaddr)
        activation_url = "http://127.0.0.1/members/activate/" + activation_key
        data = dict (first_name = first_name, activation_url = activation_url)
        mail_data = messaging.activation.create_message(data)
        if sendmail:
            env.mailer.send(**mail_data)
        return registered.id
    new.exec_mode = constants.exec_modes.BG

    def info(self, activation_key):
        member = registered_store.fetch_one_by(activation_key=activation_key)
        if not member:
            raise erros.APIExecutionError("Invalid/Expired Activation key")
        return registered_store.obj2dict(member)

    def activate(activation_key, **member_data):
        activation_info = get_activation_info(activation_key)
        member_data.update(activation_info)
        member_data.pop('activation_key')
        member_data.pop('ipaddr')
        member_id = add(**member_data)
        return member_id


class Members(bases.app.Collection):
    methods_available = ['new', 'list', 'search']
    def new(self, username, password, enabled, email, address=None, city=None, country=None, pincode=None, organization=None, home_no=None, mobile_no=None, fax_no=None, skype_name=None, sip_id=None, website=None, first_name=None, last_name=None, short_description=None, long_description=None, twitter_handle=None, facebook_name=None, blog=None, linkedin_contact=None, use_gravtar=None):
        member = memberstore.add(username, password, enabled, email, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website, first_name, last_name, short_description, long_description, twitter_handle, facebook_name, blog, linkedin_contact, use_gravtar)
        return member.id
    def search(self, crit):
        return 'TEST'

class ProfileMethods(bases.app.ObjectMethods):
    pass

class ContactMethods(bases.app.ObjectMethods):
    pass

profile_methods = ProfileMethods(profilestore)
contact_methods = ContactMethods(contactstore)

class MemberMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'get', 'set']
    get_attributes = ['profile', 'contact']
    contained_items = dict(profile=profile_methods, contact=contact_methods, user=userslib.user_methods)
    contained = contained_items.keys()

    def info(self, member_id):
        member = memberstore.fetch_by_id(member_id)
        return memberstore.obj2dict(member)
    #info.perms = OR(EQ(match_cuser('member_id')), 'biz:<cuser_biz>::host')

    def get(self, member_id, attr):
        member = memberstore.fetch_by_id(member_id)
        return profilestore.obj2dict(getattr(member, attr))

    def set(self, member_id, attr, v):
        mod_data = {attr: v}
        memberstore.edit(member_id, mod_data)
        return True

    def update(self, member_id, mod_data):
        memberstore.edit(member_id, mod_data)

class MeMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'update', 'get', 'set']
    get_attributes = ['profile', 'contact']
    set_attributes = ['profile', 'contact']

    def info(self):
        member_id = env.context.user_id
        return member_methods.info(member_id)

    def get(self, attr):
        member_id = env.context.user_id
        return member_methods.get(member_id, attr)

    def set(self, attr, v):
        member_id = env.context.user_id
        return member_methods.set(member_id, attr, v)

    def update(self, mod_data):
        member_id = env.context.user_id
        return member_methods.update(member_id, mod_data)

members = Members(memberstore)
me_methods = MeMethods()
member_methods = MemberMethods(memberstore)
