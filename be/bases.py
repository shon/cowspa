from functools import wraps, update_wrapper
import wrappers as wrapperslib
import abc

class BaseStore(object):
    __metaclass__ = abc.ABCMeta

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

class BaseDispatcher(object):
    pass

class PyroDispatcher(BaseDispatcher):
    pass

wrappers = ( ('validator', wrapperslib.validator),
             ('console_debug', wrapperslib.console_debugger),
        )

class Command(object):
    def __init__(self, f):
        update_wrapper(self, f)
        f_orig = f
        for prop, wrapper in wrappers:
            if getattr(f_orig, prop, None):
                f = wrapper(f)
                update_wrapper(f, f_orig)
        self.f = f
    def __call__(self, *args, **kw):
        res = self.f(*args, **kw)
        return res

class APINode(object):
    def __init__(self):
        self.apis = {}
        self.nodes = {}
    def add_api(self, api, name=None):
        name = name or api.__name__
        setattr(self, name, api)
        self.apis[name] = api
    def add_node(self, name, node):
        setattr(self, name, node)
        self.nodes[name] = node
    def __repr__(self):
        s = str( self.apis.keys() or '' )
        for name, node in self.nodes.items():
            s += (name + '\n')
            s += (str(node) + '\n')
        return s

class Application:
    def __init__(self):
        self.root = APINode()
    def __repr__(self):
        return str(self.root)
