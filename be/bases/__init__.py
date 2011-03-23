import abc
from functools import wraps, update_wrapper

from commonlib.helpers import odict
import wrappers as wrapperslib
import errors

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


class BaseDispatcher(object):
    pass

class PyroDispatcher(BaseDispatcher):
    pass

wrappers = ( ('validator', wrapperslib.validator),
             ('console_debug', wrapperslib.console_debugger),
        )

class APIExecutor(object):
    def __init__(self, target, api_proxy):
        update_wrapper(self, target)
        f = target
        for prop, wrapper in wrappers:
            if getattr(api_proxy, prop, None):
                f = wrapper(f)
                update_wrapper(f, target)
        self.f = f
    def __call__(self, *args, **kw):
        retcode = errors.complete_retcode
        try:
            res = self.f(*args, **kw)
        except errors.APIExecutionError, err:
            retcode = errors.execution_error
            res = err.msgs
        except Exception, err:
            retcode = getattr(err, 'suggested_retcode', errors.exception_retcode)
            res = getattr(err, 'suggested_result', str(err))
        #return retcode, res
        return {'retcode': retcode, 'result': res}

sep = '/'

# Would TreeDict help? http://www.stat.washington.edu/~hoytak/code/treedict/api.html

class odict(odict):
    def __call__(self, *args, **kw):
        return self['target'](*args, **kw)

class Application(odict):
    def add_api(self, api):
        path_comps = api.path.split(sep)
        current = self
        path_len = len(path_comps)
        for idx, comp in enumerate(path_comps, 1):
            reached_end = idx == path_len
            if not reached_end:
                current.setdefault(comp, odict())
                current = current[comp]
            else:
                current[comp] = odict()
                current[comp]['target'] = api
                if api.validator:
                    current[comp]['validator'] = odict()
                    current[comp]['validator']['target'] = api.validator

class APISpec(object):
    path = ''
    validator = None
    def __init__(self, target):
        self.target = APIExecutor(target, self)
    def __call__(self, *args, **kw):
        res = self.target(*args, **kw)
        return res

def guess_type(s):
    if s.isdigit():
        return 'int'
    elif s.isalnum():
        return 'str'
    else:
        raise Exception('Unknown format: ' + s)

def navigate_slashed_path(app, path, *args, **kw):
    comps = path.split(sep)
    this = app
    for comp in comps:
        next_ = this.get(comp)
        if not next_:
            comp_type = guess_type(comp)
            keys = [k for k in this.keys() if k.startswith('<' + comp_type + ':')]
            if keys:
                for key in keys:
                    if comp_type in key: break
                else:
                    raise Exception('No handler for format: ' + comp_type)
                this = this[key]
                next_ = this
                varname = key.split(':')[-1][:-1]
                if comp_type == 'int':
                    kw[varname] = int(comp)
                elif comp_type == 'str':
                    kw[varname] = comp
            else:
                raise Exception('Unable to find path component: ' + comp)
        else:
            this = next_
    return next_(*args, **kw)
