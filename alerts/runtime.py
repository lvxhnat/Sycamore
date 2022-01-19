from functools import wraps
from time import time


def logruntime(loggingfn):
    """ Decorator for measuring function runtime with logging support
    """
    def timeit(f):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            loggingfn('Function: %r took: %2.4f sec' % (f.__name__, te-ts))
            return result
        return wrap
    return timeit
