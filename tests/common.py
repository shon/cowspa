import datetime

def timer(fn, args=[], n=1):
    start = datetime.datetime.now()
    for x in xrange(n):
        fn(*args)
        if n % 1000: print n
    return datetime.datetime.now() - start


