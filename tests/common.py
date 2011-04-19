import datetime

def timer(fn, args=[], n=1):
    start = datetime.datetime.now()
    for x in xrange(n):
        fn(*args)
    return datetime.datetime.now() - start


