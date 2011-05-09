import bases
import be.libs.signals as signals
import be.repository.stores as stores

biz_store = stores.biz_store
plan_store = stores.plan_store

class Biz(bases.app.Collection):
    methods_available = ['new', 'list']
    def new(self, name, city, director_id=None, short_description=None, long_description=None, tags=[], website=None, twitter=None, facebook=None, blog=None, linkedin=None, enabled=True):
        biz = self.store.add(name=name, city=city, short_description=short_description, long_description=long_description, tags=tags, website=website, twitter=twitter, facebook=facebook, blog=blog, linkedin=linkedin, enabled=enabled)
        if not director_id:
            director_id = env.context.user_id
        signals.send_signal('assign_roles', director_id, biz.id, ['host'])
        return biz.id
    def list(self):
        attrs_to_include = ('id', 'name', 'city')
        compact = lambda o: dict((a, getattr(o, a)) for a in attrs_to_include)
        return [compact(b) for b in self.store.fetch_all()]

class BizMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'plans']
    id_name = 'biz_id'
    def plans(self, biz_id):
        plans = plan_store.fetch_by(biz_id=biz_id)
        return [plan_store.obj2dict(plan) for plan in plans]

biz = Biz(biz_store)
biz_methods = BizMethods(biz_store)
signals.connect("newbiz_approved", biz.new)
