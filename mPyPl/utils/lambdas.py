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
