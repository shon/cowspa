import be.repository.stores as stores

biz_store = stores.biz_store

def add(name):
    return biz_store.add(name=name).id
