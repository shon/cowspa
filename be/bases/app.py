from functools import wraps, update_wrapper

import errors

class BaseDispatcher(object):
    pass

class PyroDispatcher(BaseDispatcher):
    pass

# Would TreeDict help? http://www.stat.washington.edu/~hoytak/code/treedict/api.html

class API(object):
    def __init__(self, target, branch):
        update_wrapper(self, target)
        f = target
        for wrapper in branch.top.api_wrappers:
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
            retcode = getattr(err, 'suggested_retcode', errors.exception_retcode)
            res = getattr(err, 'suggested_result', str(err))
        return {'retcode': retcode, 'result': res}

def dummy_handler(*args, **kw):
    return None

sep = '.'

class Tree(dict):
    def __init__(self, path='', *args, **kw):
        self.path = path
        self['parent'] = None
        self.api_wrappers = []
        if not path: # top
            self.top = self
        dict.__init__(self, *args, **kw)
    def register_api_wrappers(self, wrappers):
        self.api_wrappers = wrappers
    def register_session_lookup(self, lookuper):
        self.session_lookuper = lookuper
    def add_branch(self, handler=dummy_handler, name=''):
        if not name:
            name = handler.__name__
        path = sep.join((self.path, name))
        branch = Tree(path)
        branch['handler'] = API(handler, self) # important transformation
        branch['top'] = self.top
        #branch['parent'] = self
        if name.startswith('int:'):
            self['int_handler'] = branch
            branch['varname'] = name.split(':')[-1]
        elif name.startswith('str:'):
            self['str_handler'] = branch
            branch['varname'] = name.split(':')[-1]
        else:
            self[name] = branch
        return branch
    def add_session_maker(self, session_maker):
        self.session_maker = session_maker
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
        return ret
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
    def set_context(self, auth_token):
        print "set_context"
        env.context.user_id = self._tree.session_lookuper(auth_token)
        print "set_context", env.context.user_id
    def __getattr__(self, name):
        return Traverser(self._tree)
    def __getitem__(self, name):
        return Traverser(self._tree)
