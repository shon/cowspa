import bases
import be.repository.stores as stores

biz_store = stores.biz_store

class Biz(bases.app.Collection):
    methods_available = ['new']
    def new(self, name):
        return self.store.add(name=name).id


biz = Biz(biz_store)
