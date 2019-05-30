# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import types
import numpy as np

def getattritem(o,a):
    """
    Get either attribute or item `a` from a given object `o`. Supports multiple evaluations, for example
    `getattritem(o,'one.two')` would get `o.one.two`, `o['one']['two']`, etc.
    :param o: Object
    :param a: Attribute or Item index. Can contain `.`, in which case the final value is obtained.
    :return: Value
    """
    flds = a.split('.')
    for x in flds:
        if x in dir(o):
            o = getattr(o,x)
        else:
            o = o[x]
    return o

def enlist(x):
    """
    Make sure that the specified value is a list. If it's a list - returns it unchanged. If it's a value, returns
     a list with this value.
    :param x: input value
    :return: list
    """
    if isinstance(x, list):
        return x
    elif isinstance(x,types.GeneratorType):
        return list(x)
    else:
        return [x]

def entuple(x,n=2):
    """
    Make sure given value is a tuple. It is useful, for example, when you want to provide dimentions of an image either
    as a tuple, or as an int - in which case you can use `(w,h) = entuple(x)`.
    :param x: Either atomic value or a tuple. If the value is atomic, it is converted to a tuple of length `n`. It the value
    is a tuple - it is inchanged
    :param n: Number of elements in a tuple
    :return: Tuple of a specified size
    """
    if type(x) is tuple:
        return x
    elif type(x) is list:
        return tuple(x)
    else:
        return tuple([x]*n)

def print_decorate(msg,expr):
    """
    Helper function to make a print decoration around lambda expression. It will print `msg`, and then return
    the result of `expr`. If it typically used in expressions like
    `lambda x: print_decorate("Processing {}".format(x), do_smth_with(x))`
    :param msg: Message to print
    :param expr: Expression to compute
    :return: expr
    """
    print(msg)
    return expr


def unzip_list(x):
    u, v = zip(*x)
    return list(u), list(v)


# TODO: Consider moving to separate file
def normalize_npy(x,interval=(0,1)):
    """
    Normalize specified numpy array to be in the given inteval
    :param x: Input array
    :param interval: Interval tuple, defaults to (0,1)
    :return: Normalized array
    """
    mi = np.min(x)
    ma = np.max(x)
    return (x-mi)/(ma-mi)*(interval[1]-interval[0])+interval[0]
