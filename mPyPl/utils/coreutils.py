# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

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
