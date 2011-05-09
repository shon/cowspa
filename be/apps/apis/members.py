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

create_activation_key = commonlib.helpers.random_key_gen

class Registrations(bases.app.Collection):
    methods_available = ['new', 'activate', 'by_id']
    def new(self, first_name, last_name, email, ipaddr=None, sendmail=True):
        activation_key = create_activation_key()
        registered = self.store.add(activation_key, first_name, last_name, email, ipaddr)
        activation_url = env.config.http_baseurl + "/activate#" + activation_key
        author = ('Cowspa activation service', 'cowspa.dev@gmail.com')
        data = dict (author=author, to=(first_name, email), first_name=first_name, activation_url=activation_url)
        mail_data = messaging.activation.create_message(data)
        if sendmail:
            env.mailer.send(**mail_data)
        return registered.id
    new.exec_mode = constants.exec_modes.BG

    def by_id(self, id):
        return self.store.obj2dict(self.store.fetch_by_id(id))

    def info(self, activation_key):
        member = self.store.fetch_one_by(activation_key=activation_key)
        if not member:
            raise erros.APIExecutionError("Invalid/Expired Activation key")
        return self.store.obj2dict(member)

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
    if memberstore.fetch_by_id(1):
        raise Exception("Existing User detected")
    member_id = members.new(username, password, True, email, first_name=first_name, last_name=last_name)
    assert int(member_id) == 1
    userslib.user_methods.assign_roles(username, None, ['admin'])
    return True

class Members(bases.app.Collection):
    methods_available = ['new', 'list', 'search']
    def new(self, username, password, enabled, email, language='en', display_name=None, address=None, city=None, country=None, pincode=None, organization=None, home_no=None, mobile_no=None, fax_no=None, skype_name=None, sip_id=None, website=None, first_name=None, last_name=None, short_description=None, long_description=None, twitter=None, facebook=None, blog=None, linkedin=None, use_gravtar=None):
        if not display_name:
            display_name = first_name + ' ' + last_name
        member = memberstore.add(username, password, enabled, email, language, display_name, address, city, country, pincode, organization, home_no, mobile_no, fax_no, skype_name, sip_id, website, first_name, last_name, short_description, long_description, twitter, facebook, blog, linkedin, use_gravtar)
        search_d = self.member2searchdict(member)
        searchlib.add(search_d)
        return member.id
    def member2searchdict(self, member):
        profile = member.profile
        d = dict((attr, getattr(profile, attr)) for attr in ('display_name', 'short_description', 'long_description'))
        d['id'] = unicode(member.id)
        d['username'] = member.user.username
        return d


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
        member = memberstore.fetch_by_id(member_id)
        return memberstore.obj2dict(member)
    #info.perms = OR(EQ(match_cuser('member_id')), 'biz:<cuser_biz>::host')

    def get(self, member_id, attr):
        member = memberstore.fetch_by_id(member_id)
        d = profilestore.obj2dict(getattr(member, attr))
        d['member_id'] = member_id
        return d

    def set(self, member_id, attr, v):
        mod_data = {attr: v}
        memberstore.edit(member_id, mod_data)
        return True

    def update(self, member_id, mod_data):
        memberstore.edit(member_id, mod_data)

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
        role_ids = user_roles_store.fetch_one_by(user_id=member_id).role_ids
        for role_id in role_ids:
            if not '::' in role_id: continue
            biz_id, role_id = role_id.split('::')
            biz_id = biz_id.split(':')[1]
            role_name = role_store.fetch_by_id(role_id).name
            d[biz_id][0].append(role_name)
        for plan in plan_store.fetch_by(subscribers=member_id):
            d[plan.biz_id][1].append(plan.name)
        print tuple(dict(name=biz_store.fetch_by_id(biz_id).name, roles=v[0], plans=v[1]) for biz_id, v in d.items())
        return tuple(dict(name=biz_store.fetch_by_id(biz_id).name, roles=v[0], plans=v[1]) for biz_id, v in d.items())


    def update(self, mod_data):
        member_id = env.context.user_id
        return member_methods.update(member_id, mod_data)

registrations = Registrations(registered_store)
members = Members(memberstore)
me_methods = MeMethods()
member_methods = MemberMethods(memberstore)
