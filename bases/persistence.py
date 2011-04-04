import abc
import datetime

from commonlib.helpers import odict

class BaseStore(object):
    __metaclass__ = abc.ABCMeta

    def ref(self, obj):
        return obj.__class__.__name__ + ':' + str(obj.id)

    @abc.abstractmethod
    def add(self, **data):
        """
        returns oid
        """

    @abc.abstractmethod
    def remove(self, oids):
        """
        """

    @abc.abstractmethod
    def edit(self, oid, mod_data):
        """
        """

    @abc.abstractmethod
    def list(self, limit=None, order_by=None):
        """
        """

    @abc.abstractmethod
    def fetch_by(self, **crit):
        """
        """

    @abc.abstractmethod
    def fetch_by_id(self, oid):
        """
        """

    @abc.abstractmethod
    def fetch_one_by(self, **crit):
        """
        """

    def soft_fetch_one_by(self, *args, **kw):
        """
        returns None if not found
        """
        try:
            return self.fetch_one_by(*args, **kw)
        except IndexError, err:
            pass

    @abc.abstractmethod
    def obj2dict(self, obj):
        """
        returns dictionary created with attribute names and values
        """

class CachedStore(BaseStore):
    def __init__(self, store, *args, **kw):
        self.store = store
        self._cache_by_id = dict((o.id, odict(self.store.obj2dict(o))) for o in self.store.model.objects.all())
        for k,v in self._cache_by_id.items():
            v['id'] = k
    def add(self, *args, **kw):
        obj = self.store.add(*args, **kw)
        self._cache_by_id[obj.id] = odict(self.store.obj2dict(obj))
        self._cache_by_id[obj.id]['id'] = obj.id
        return obj
    def edit(self, oid, mod_data):
        raise NotImplemented # unless we take care of cache invalidation
    def list(self, limit=None, order_by=None):
        raise NotImplemented
    def fetch_one_by(self, **crit):
        for d in self._cache_by_id.values():
            if all((v==d[k]) for k,v in crit.items()):
                return d
        else:
            raise IndexError("No match")
    def fetch_by(self, **crit):
        return tuple(d for d in self._cache_by_id.values() if \
            all(((k,v)==(d[k])) for k,v in crit.items()))
    def fetch_by_id(self, oid):
        return self._cache_by_id[oid]
    def remove(self, oid):
        raise NotImplemented # unless we take care of cache invalidation
    def obj2dict(self, obj):
        return self._cache_by_id[obj.id]

class RedisStore(BaseStore):
    def add(self, **data):
        """
        returns oid
        """
        raise NotImplemented

    def edit(self, oid, mod_data):
        """
        """

    def list(self, limit=None, order_by=None):
        """
        """
        raise NotImplemented

    def fetch_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)

    def fetch_one_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)[0]

    def fetch_by_id(self, oid):
        """
        """
        return self.model.objects.get_by_id(oid)

    def remove(self, oid):
        obj = self.model.objects.filter(id=oid)[0]
        return obj.delete()

    @classmethod
    def obj2dict(self, obj):
        d = {}
        for k, v in obj.attributes_dict.items():
            if isinstance(v, datetime.datetime):
                v = v.isoformat()
            d[k] = v
        return d


