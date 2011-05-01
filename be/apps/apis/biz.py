import bases
import be.repository.stores as stores

biz_store = stores.biz_store
plan_store = stores.plan_store

class Biz(bases.app.Collection):
    methods_available = ['new', 'list']
    def new(self, name):
        return self.store.add(name=name).id
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
