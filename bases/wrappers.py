import inspect
#import pycerberus
import errors

#import be.repository.stores as stores

#session_store = stores.session_store

def session_maker(f):
    if cs_context.auth_token:
        user_id = session_store.fetch_one_by(session=auth_token).user_id
        cs_context.permissions = pp
        cs_context.user_id = user_id
def console_debugger(f):
    def wrapper(*args, **kw):
        print f.__name__, 'called with :', args, kw
        res = f(*args, **kw)
        print f.__name__, 'returned :', res
        return res
    return wrapper

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
