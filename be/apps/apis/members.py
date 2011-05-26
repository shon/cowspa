import datetime
import collections

import bases
import bases.constants as constants
import be.repository.stores as stores
import be.libs.search as searchlib

import commonlib
import commonlib.messaging.email as emaillib
import commonlib.messaging as messaging

import users as userslib

memberstore = stores.memberstore
profilestore = stores.profilestore
registered_store = stores.registered_store
contactstore = stores.contactstore
user_roles_store = stores.user_roles_store
role_store = stores.role_store
plan_store = stores.plan_store
biz_store = stores.biz_store
memberpref_store = stores.memberpref_store

create_activation_key = commonlib.helpers.random_key_gen

class Member(object):
    def __init__(self, m_id):
        self.m_id = m_id
    @property
    def profile(self):
        return profilestore.get_one_by(member=self.m_id)
    @profile.setter
    def profile(self, mod_data):
        profilestore.update_by(crit={'member':self.m_id}, **mod_data)
    @property
    def contact(self):
        return contactstore.get_one_by(member=m_id)
    @contact.setter
    def contact(self, mod_data):
        ref = memberstore.ref(self.m_id)
        contactstore.update_by(crit={'owner':ref}, mod_data=mod_data)
    @property
    def pref(self):
        return memberpref_store.get_one_by(member=self.m_id)
    @pref.setter
    def pref(self, mod_data):
        return memberpref_store.update_by(crit={'member':self.m_id}, **mod_data)

class Registrations(bases.app.Collection):
    methods_available = ['new', 'activate', 'by_id']
    def new(self, first_name, last_name, email, ipaddr=None, sendmail=False):
        activation_key = create_activation_key()
        registered_id = self.store.add(activation_key, first_name, last_name, email, ipaddr)
        activation_url = env.config.http_baseurl + "/activate#" + activation_key
        author = ('Cowspa activation service', 'cowspa.dev@gmail.com')
        data = dict (author=author, to=(first_name, email), first_name=first_name, activation_url=activation_url)
        mail_data = messaging.activation.create_message(data)
        if sendmail:
            env.mailer.send(**mail_data)
        return registered_id
    new.exec_mode = constants.exec_modes.BG

    def by_id(self, id):
        return self.store.get(id)

    def info(self, activation_key):
        member = self.store.get_one_by(activation_key=activation_key)
        if not member:
            raise erros.APIExecutionError("Invalid/Expired Activation key")
        return member

    def activate(self, activation_key, **member_data):
        activation_info = self.info(activation_key)
        member_data.update(activation_info)
        member_data.pop('activation_key')
        member_data.pop('ipaddr')
        member_data.pop('id')
        member_data['enabled'] = True
        member_data['display_name'] = "%(first_name)s %(last_name)s" % member_data
        member_id = members.new(**member_data)
        return member_id

def addsuperuser(first_name, last_name, username, password, email):
    if memberstore.get(1):
        raise Exception("Existing User detected")
    member_id = members.new(username, password, True, email, first_name=first_name, last_name=last_name)
    assert int(member_id) == 1
    userslib.user_methods.assign_roles(username, None, ['admin'])
    return True

class Members(bases.app.Collection):
    methods_available = ['new', 'list', 'search']
    def new(self, username, password, enabled, email, language='en', display_name=None, address=None, city=None, country=None, pincode=None, homephone=None, mobile=None, fax=None, skype=None, sip=None, website=None, first_name=None, last_name=None, short_description=None, long_description=None, twitter=None, facebook=None, blog=None, linkedin=None, use_gravtar=None):
        if not display_name: display_name = first_name + ' ' + last_name
        created = datetime.datetime.now()

        user_id = stores.userstore.add(username, password, enabled)
        member_ref = memberstore.ref(user_id)
        contact_id = contactstore.add(member_ref, email, address, city, country, pincode, homephone, mobile, fax, skype, sip)
        profilestore.add(user_id, first_name, last_name, display_name, short_description, long_description, website, twitter, facebook, blog, linkedin, use_gravtar)
        stores.memberpref_store.add(user_id, language=language)
        self.store.add(id=user_id, contact_id=contact_id, created=created)

        search_d = dict(id=user_id, display_name=display_name, short_description=short_description, long_description=long_description, username=username)
        searchlib.add(search_d)
        return user_id

    def search(self, crit):
        return 'TEST'

class ProfileMethods(bases.app.ObjectMethods):
    social_attrs = ('twitter', 'facebook', 'blog', 'linkedin')

class ContactMethods(bases.app.ObjectMethods):
    pass

profile_methods = ProfileMethods(profilestore)
contact_methods = ContactMethods(contactstore)

class MemberMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'get', 'set']
    get_attributes = ['profile', 'contact', 'pref']
    contained_items = dict(profile=profile_methods, contact=contact_methods, user=userslib.user_methods)
    contained = contained_items.keys()

    def info(self, member_id):
        return memberstore.get(member_id)
    #info.perms = OR(EQ(match_cuser('member_id')), 'biz:<cuser_biz>::host')

    def get(self, member_id, attr):
        member = Member(member_id)
        return getattr(member, attr)

    def set(self, member_id, attr, v):
        member = Member(member_id)
        setattr(member, attr, v)
        return True

class MeMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'update', 'get', 'set', 'memberships']
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

    def memberships(self):
        member_id = env.context.user_id
        d = collections.defaultdict(lambda: ([], []))
        role_ids = user_roles_store.get_one_by(user_id=member_id).role_ids
        for role_id in role_ids:
            if not '::' in role_id: continue
            biz_id, role_id = role_id.split('::')
            biz_id = biz_id.split(':')[1]
            role_name = role_store.get(role_id).name
            d[biz_id][0].append(role_name)
        for plan in plan_store.get_by(subscribers=member_id):
            d[plan.biz_id][1].append(plan.name)
        return tuple(dict(name=biz_store.get(biz_id).name, roles=v[0], plans=v[1]) for biz_id, v in d.items())

registrations = Registrations(registered_store)
members = Members(memberstore)
me_methods = MeMethods()
member_methods = MemberMethods(memberstore)
