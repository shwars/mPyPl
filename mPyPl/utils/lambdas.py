# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Useful lambdas

id = lambda x:x

def dict_lookup(dict):
    """
    Lookup a value in dictionary
    :param dict: Dictionary to use
    :return: Lambda-function to perform the lookup in the dictionary
    """
    return lambda x: dict[x]

def enfunc(x):
    """
    So-called K combinator. Given any value `x`, returns a function, that for any
    input value returns `x`
    :param x: value to be returned
    :return: function that returns `x` for any input
    """
    return lambda _ : x
