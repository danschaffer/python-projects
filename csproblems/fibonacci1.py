#!/usr/bin/env python
import sys
import time
def timeit(f):

    def format_time(secs: float) -> str:
        res = ''
        if secs > 60*60:
            res = str(secs//(60*60)) + 'h'
        if secs > 60:
            res = res + (secs//60) + 'm'
        res = "%.2f" % secs
        return res

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %s' % (f.__name__, args, kw, format_time(te-ts)))
        return result

    return timed

@timeit    
def fibonacci1(n: int) -> int:
    return fib1(n)

def fib1(n: int) -> int:
    if n < 2:
        return n
    return fib1(n-1) + fib1(n-2)

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print(f"{arg} ->  {fibonacci1(int(arg))}")
