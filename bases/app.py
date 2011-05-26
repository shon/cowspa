import traceback
import inspect
from functools import wraps, update_wrapper, partial
import functools

import werkzeug.exceptions
import werkzeug.routing as routing

import persistence
import errors

class http_methods:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

class API(object):
    def __init__(self, target, api_wrappers):
        update_wrapper(self, target)
        f = target
        for wrapper in api_wrappers:
            target_pref = getattr(target, wrapper.prop, None)
            if target_pref is None: target_pref = getattr(wrapper, 'default', None)
            if target_pref:
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
            print "UNCAUGHT EXCEPTION"
            traceback.print_exc()
            retcode = getattr(err, 'suggested_retcode', errors.exception_retcode)
            res = getattr(err, 'suggested_result', str(err))
        return {'retcode': retcode, 'result': res}

class Mapper(object):
    def __init__(self, prefix=''):
        self.prefix = prefix if prefix[0] is '/' else '/' + prefix
        self.rules = []
    def add_api_factory(self, api_factory):
        self.api_factory = api_factory
    def append_rule(self, path, endpoint, methods=None):
        endpoint = self.api_factory(endpoint)
        path = self.prefix + '/' + path
        if not methods:
            self.rules.append(routing.Rule(path, endpoint=endpoint))
            #print path, endpoint
        else:
            #print path, endpoint, methods
            self.rules.append(routing.Rule(path, endpoint=endpoint, methods=methods))
    def connect(self, path, function=None):
        if callable(path):
            function = path
            path = function.__name__
        self.append_rule(path, function)
    def connect_collection(self, prefix, collection, add_rest_support=True):
        if not isinstance(collection, Collection):
            raise TypeError("Typs mismatch: %s is not instance of Collection" % collection)
        for name in collection.methods_available:
            method = getattr(collection, name)
            self.append_rule(prefix +'/' + name, method)
            if add_rest_support and name in collection.supported_rest_config:
                http_method, subpath = collection.supported_rest_config[name]
                self.append_rule(prefix + subpath, method, [http_method])
    def connect_object_methods(self, prefix, o_mehtods, add_rest_support=True):
        if not isinstance(o_mehtods, ObjectMethods):
            raise TypeError("Typs mismatch: %s is not instance of ObjectMethods" % o_mehtods)
        for name in o_mehtods.methods_available:
            method = getattr(o_mehtods, name)
            self.append_rule(prefix + '/' + name, method)
            if add_rest_support and name in o_mehtods.supported_rest_config:
                http_method, subpath = o_mehtods.supported_rest_config[name]
                self.append_rule(prefix + subpath, method, [http_method])
        if add_rest_support and 'get' in o_mehtods.methods_available:
            self.append_rule(prefix + '/<attr>', o_mehtods.get, [http_methods.GET])
        if add_rest_support and 'set' in o_mehtods.methods_available:
            def set_a(**kw):
                args = inspect.getargspec(o_mehtods.set).args[1:-1]
                try:
                    args_extracted = [kw.pop(arg) for arg in args]
                    args_extracted.append(kw)
                except KeyError:
                    raise TypeError('some of the arguments (%s) are missing' % str(args))
                return o_mehtods.set(*args_extracted)
            self.append_rule(prefix + '/<attr>', set_a, [http_methods.POST])

        ## One more way to map get/set atrribute URLs, here we don't have keywaords embedded in the URL but have generated functions per attribute
        #if add_rest_support and 'get' in o_mehtods.methods_available:
        #    for name in o_mehtods.get_attributes:
        #        def get(name):
        #            return lambda **kw: o_mehtods.get(attr=name, **kw)
        #        self.append_rule(prefix + '/' + name, get(name), [http_methods.GET])
        #if add_rest_support and 'set' in o_mehtods.methods_available:
        #    for name in o_mehtods.set_attributes:
        #        def set_a(name):
        #            return lambda **kw: o_mehtods.set(name, v=kw)
        #        self.append_rule(prefix + '/' + name, set_a(name), [http_methods.POST])

    def build(self):
        m = routing.Map(self.rules)
        return m.bind("cowspa.net", "/")


class Collection(object):
    supported_rest_config = dict(
            list = (http_methods.GET, ''),
            filter = (http_methods.POST, '/'),
            new = (http_methods.POST, '/new'),
            delete_all = (http_methods.DELETE, '/'),
            bulk_add = (http_methods.PUT, '/'))
    def __init__(self, store):
        if not isinstance(store, persistence.BaseStore):
            raise TypeError("Typs mismatch: %s is not instance of persistence.Store" % store)
        self.store = store
    def list(self):
        return self.store.get_all()
    def new(self):
        raise NotImplemented
    def search(self, crit):
        raise NotImplemented
    def delete_all(self):
        raise NotImplemented

class ObjectMethods(object):
    supported_rest_config = dict(
        info = (http_methods.GET, ''),
        update = (http_methods.POST, ''))
    get_attributes = []
    set_attributes = []
    id_name = 'oid'
    def __init__(self, store=None):
        if store:
            if not isinstance(store, persistence.BaseStore):
                raise TypeError("Typs mismatch: %s is not instance of persistence.Store" % store)
            self.store = store
    def info(self, *args, **kw):
        oid = kw.get(self.id_name)
        return self.store.get(oid)
    info.console_debug = True
    def details(self, oid):
        oid = kw.get(self.id_name)
        return self.store.get(oid)
    def delete(self, oid):
        raise NotImplemented
    def get(self, *args, **kw):
        oid = kw.get(self.id_name)
        attr = kw['attr']
        o = self.store.get(oid)
        return getattr(o, attr)
    def set(self, *args, **kw):
        oid = kw.get(self.id_name)
        attr = kw['attr']
        o = self.store.get(oid)
        setattr(o, attr, kw['v'])
    def update(self, oid, mod_data):
        self.store.update(oid, mod_data)
        return True

class Traverser(object):
    def __init__(self, tree):
        self.path = []
        self.tree = tree

class PyTraverser(Traverser):
    def __getattr__(self, name):
        self.path.append(name)
        return self
    def __getitem__(self, name):
        if not isinstance(name, basestring):
            name = str(name)
        self.path.append(name)
        return self
    def __call__(self, *args, **kw):
        path = '/' + '/'.join(self.path)
        try:
            f, _kw = self.tree.match(path)
            kw.update(_kw)
        except werkzeug.exceptions.NotFound:
            raise Exception("Handler for %s not found" % path)
        return f(*args, **kw)

class HTTPTraverser(Traverser):
    def __call__(self, path, http_method='GET', data={}):
        path = '/' + path
        try:
            f, kw = self.tree.match(path, http_method)
            data.update(kw)
        except werkzeug.exceptions.NotFound:
            raise Exception("Handler for %s not found" % path)
        return f(**data)

class TraverserFactory(object):
    def __init__(self, Traverser, tree):
        self._traverser = Traverser
        self._tree = tree
    def __getattr__(self, name):
        return self._traverser(self._tree)
    def __getitem__(self, name):
        return self._traverser(self._tree)

class Application(object):
    def __init__(self, name):
        self.name = name
        self.on_startup = []
        self.on_shutdown = []
        self.session_lookup = None
        self.tree  = None
    @property
    def root(self):
        return PyTraverser(self.tree)
    @property
    def http(self):
        return HTTPTraverser(self.tree)
    def startup(self):
        for f in self.on_startup:
            f()
            print self.name, ':startup::', f.__func__.__module__, '.', f.__name__
    def shutdown(self):
        # sys.atexit
        for f in self.on_shutdown:
            f()
    def set_context(self, auth_token):
        env.context.user_id = self.session_lookup(auth_token)
