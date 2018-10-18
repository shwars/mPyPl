
# Lazy Dictionary class to be used for computations

class LazyDict(dict):
    """
    Lazy Dictionary class that supports field evaluation upon request
    """
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)

    def __getitem__(self, item):
        res = dict.__getitem__(self,item)
        if callable(res):
            res = res.__call__()
            self[item] = res
        return res

    def get(self, item):
        return dict.__getitem__(self,item)
