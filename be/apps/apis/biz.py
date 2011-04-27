import bases
import be.repository.stores as stores

biz_store = stores.biz_store
plan_store = stores.plan_store

class Biz(bases.app.Collection):
    methods_available = ['new']
    def new(self, name):
        return self.store.add(name=name).id

class BizMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'plans']
    id_name = 'biz_id'
    def plans(self, biz_id):
        biz_ref = 'Biz:%s' % biz_id
        plans = plan_store.fetch_by(owner=biz_ref)
        return [plan_store.obj2dict(plan) for plan in plans]


biz = Biz(biz_store)
biz_methods = BizMethods(biz_store)
