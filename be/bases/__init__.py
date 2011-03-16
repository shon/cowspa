import abc
from functools import wraps, update_wrapper

from commonlib.helpers import odict
import wrappers as wrapperslib
import errors

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
    @abc.abstractmethod
    def obj2dict(self, obj):
        """
        returns dictionary created with attribute names and values
        """

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
            print err
            retcode = getattr(err, 'suggested_retcode', errors.exception_retcode)
            res = getattr(err, 'suggested_result', str(err))
        return retcode, res
        return {'retcode': retcode, 'result': res}

sep = '/'

# Would TreeDict help? http://www.stat.washington.edu/~hoytak/code/treedict/api.html

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
    elif s.isalpha():
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
                key = keys[0]
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
    return next_['target'](*args, **kw)
