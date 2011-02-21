import inspect

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
        f.validator.process(inp_flat)
        res = f(*args, **kw)
        return res
    return wrapper

def taskmaker(f):
    return f
