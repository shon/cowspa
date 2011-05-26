import datetime

import bases
import be.libs.signals as signals
import be.repository.stores as stores

biz_store = stores.biz_store
bizplace_store = stores.bizplace_store
plan_store = stores.plan_store

class Biz(bases.app.Collection):
    methods_available = ['new', 'list']

    def new(self, name, email, address=None, city=None, country=None, pincode=None, mobile=None, fax=None, skype=None, sip=None, director_id=None, short_description=None, long_description=None, tags=[], website=None, twitter=None, facebook=None, blog=None, linkedin=None, enabled=True):
        biz_id = self.store.add(name=name, created=datetime.datetime.now(), enabled=enabled)
        biz_ref = self.store.ref(biz_id)
        homephone = None
        contact_id = stores.contactstore.add(biz_ref, email, address, city, country, pincode, homephone, mobile, fax, skype, sip)
        self.store.update(biz_id, contact=contact_id)
        stores.bizprofile_store.add(short_description, long_description, tags, website, twitter, facebook, linkedin, blog)
        if not director_id:
            director_id = env.context.user_id
        signals.send_signal('assign_roles', director_id, biz_id, ['host'])
        return biz_id

    def list(self):
        attrs_to_include = ('id', 'name', 'city')
        compact = lambda o: dict((a, getattr(o, a)) for a in attrs_to_include)
        return [compact(b) for b in self.store.get_all()]

class BizMethods(bases.app.ObjectMethods):
    methods_available = ['info']
    id_name = 'biz_id'

class Bizplaces(bases.app.Collection):
    methods_available = ['new', 'list']
    def new(self, name, city, tz, email, biz_id, enabled=True, langs=['en'], holidays=[], address=None, country=None, pincode=None, mobile=None, fax=None, skype=None, sip=None, director_id=None, short_description=None, long_description=None, tags=[], website=None, twitter=None, facebook=None, blog=None, linkedin=None):
        created = datetime.datetime.now()
        bizplace_id = self.store.add(name, enabled, created, langs, tz, holidays, biz_id)
        bizplace_ref = self.store.ref(bizplace_id)
        homephone = None
        contact_id = stores.contactstore.add(bizplace_ref, email, address, city, country, pincode, homephone, mobile, fax, skype, sip)
        self.store.update(biz_id, contact=contact_id)
        stores.bizplaceprofile_store.add(short_description, long_description, tags, website, twitter, facebook, linkedin, blog)
        if not director_id:
            director_id = env.context.user_id
        signals.send_signal('assign_roles', director_id, bizplace_id, ['host'])
        return bizplace_id

class BizplaceMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'plans']
    id_name = 'bizplace_id'
    def plans(self, bizplace_id):
        return plan_store.get_by(bizplace_id=bizplace_id)

biz = Biz(biz_store)
bizplaces = Bizplaces(bizplace_store)
biz_methods = BizMethods(biz_store)
bizplace_methods = BizplaceMethods(bizplace_store)
signals.connect("newbiz_approved", biz.new)
