import inspect
#import pycerberus
import bases.errors as errors
import be.repository.stores as stores

import apis.users as userlib

user_perms_store = stores.user_perms_store

def permission_checker(f):
    def wrapper(*args, **kw):
        user_id = env.context.user_id
        if user_id:
            permission_ids = userlib.get_user_permissions(user_id)
            print "has ", permission_ids
            print "needed", f.permissions
            # check
        res = f(*args, **kw)
        return res
    return wrapper
permission_checker.prop = "permissions"

def console_debugger(f):
    def wrapper(*args, **kw):
        print f.__name__, 'called with :', args, kw
        res = f(*args, **kw)
        print f.__name__, 'returned :', res
        return res
    return wrapper
console_debugger.prop = "console_debug"

def straighten_args(args, in_args, in_kw):
    inp = dict(zip(args, in_args))
    inp.update(in_kw)
    return inp

def validator(f):
    def wrapper(*args, **kw):
        f_args = inspect.getargspec(f).args
        inp_flat = straighten_args(f_args, args, kw)
        try:
            f.validator().process(inp_flat)
            res = f(*args, **kw)
        except pycerberus.errors.InvalidDataError, err:
            retcode = errors.validation_failed_retcode
            res = dict((k,v.message) for (k,v) in err.error_dict().items())
            raise errors.WrapperException(retcode, res)
        except Exception, err:
            raise err
        return res
    return wrapper

def taskmaker(f):
    return f
