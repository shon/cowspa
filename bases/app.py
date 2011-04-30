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
            if getattr(target, wrapper.prop, None):
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
            print path, endpoint
        else:
            print path, endpoint, methods
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
                self.append_rule(prefix + '/' + subpath, method, [http_method])
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
        return [self.store.obj2dict(o) for o in self.store.fetch_all()]
    def new(self):
        raise NotImplemented
    def search(self, crit):
        return self.store.fetch_by(**crit)
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
        o = self.store.fetch_by_id(oid)
        return self.store.obj2dict(o)
    info.console_debug = True
    def details(self, oid):
        oid = kw.get(self.id_name)
        o = self.store.fetch_by_id(oid)
        return self.store.obj2dict(o)
    def delete(self, oid):
        raise NotImplemented
    def get(self, *args, **kw):
        oid = kw.get(self.id_name)
        attr = kw['attr']
        o = self.store.fetch_by_id(oid)
        return getattr(o, attr)
    def set(self, *args, **kw):
        oid = kw.get(self.id_name)
        attr = kw['attr']
        o = self.store.fetch_by_id(plan_id)
        setattr(o, attr, kw['v'])
    def update(self, oid, mod_data):
        self.store.edit(oid, mod_data)
        return True

class Traverser(object):
    def __init__(self, app, session_lookup):
        self.path = []
        self.app = app
        self.session_lookup = session_lookup
    def set_context(self, auth_token):
        env.context.user_id = self.session_lookup(auth_token)

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
            f, _kw = self.app.match(path)
            kw.update(_kw)
        except werkzeug.exceptions.NotFound:
            raise Exception("Handler for %s not found" % path)
        return f(*args, **kw)

class HTTPTraverser(Traverser):
    def __call__(self, path, http_method='GET', data={}):
        path = '/' + path
        try:
            f, kw = self.app.match(path, http_method)
            data.update(kw)
        except werkzeug.exceptions.NotFound:
            raise Exception("Handler for %s not found" % path)
        return f(**data)

class TraverserFactory(object):
    def __init__(self, Traverser, tree, session_lookup):
        self._traverser = Traverser
        self._tree = tree
        self._session_lookup = session_lookup
    def __getattr__(self, name):
        return self._traverser(self._tree, self._session_lookup)
    def __getitem__(self, name):
        return self._traverser(self._tree, self._session_lookup)
