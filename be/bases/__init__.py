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

# Would TreeDict help? http://www.stat.washington.edu/~hoytak/code/treedict/api.html

class API(object):
    def __init__(self, target):
        update_wrapper(self, target)
        f = target
        for prop, wrapper in wrappers:
            if getattr(target, prop, None):
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
            raise
            retcode = getattr(err, 'suggested_retcode', errors.exception_retcode)
            res = getattr(err, 'suggested_result', str(err))
        return {'retcode': retcode, 'result': res}

def dummy_handler(*args, **kw):
    return None

sep = '.'

class Tree(dict):
    def __init__(self, path, *args, **kw):
        self.path = path
        self['parent'] = None
        dict.__init__(self, *args, **kw)
    def add_branch(self, handler=dummy_handler, name=''):
        if not name:
            name = handler.__name__
        path = sep.join((self.path, name))
        branch = Tree(path)
        branch['handler'] = API(handler)
        branch['parent'] = self
        if name.startswith('int:'):
            self['int_handler'] = branch
            branch['varname'] = name.split(':')[-1]
        elif name.startswith('str:'):
            self['str_handler'] = branch
            branch['varname'] = name.split(':')[-1]
        else:
            self[name] = branch
        return branch
    def __getattr__(self, name):
        return self[name]
    def __getitem__(self, name):
        if not isinstance(name, basestring):
            name = str(name)
        try:
            f = dict.__getitem__(self, name)
        except KeyError:
            f = None
        return f
    def __call__(self, *args, **kw):
        return self.handler(*args, **kw)

class Traverser(object):
    def __init__(self, app):
        self.path = []
        self.app = app
        self.args = []
        self.kw = {}
    def process_slashed_path(self, path):
        comps = (comp for comp in path.split('/') if comp)
        for comp in comps:
            ret = self[comp]
        return ret()
    def __getattr__(self, name):
        self.path.append(name)
        return self
    def __getitem__(self, name):
        if not isinstance(name, basestring):
            name = str(name)
        self.path.append(name)
        return self
    def __call__(self, *args, **kw):
        self.args.extend(args)
        self.kw.update(kw)
        cur_branch = self.app
        for comp in self.path:
            branch = getattr(cur_branch, comp, None)
            if not branch:
                if comp.isdigit():
                    branch = getattr(cur_branch, 'int_handler', None)
                    if branch:
                        self.kw[branch.varname] = comp
                else:
                    branch = getattr(cur_branch, 'str_handler', None)
                    if branch:
                        self.kw[branch.varname] = comp
            if branch:
                cur_branch = branch
            else:
                raise Exception("Handler for %s not found" % comp)
        return cur_branch(*self.args, **self.kw)
    def __str__(self):
        return str((self.path, self.args, self.kw))

class TraverserFactory(object):
    def __init__(self, tree):
        self._tree = tree
    def __getattr__(self, name):
        return Traverser(self._tree)
    def __getitem__(self, name):
        return Traverser(self._tree)
