# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Different services related to Bing search

import requests
from ..mdict import *
from .core import CognitiveService

class BingImageSearch7(CognitiveService):

    def __init__(self,key,url="https://api.cognitive.microsoft.com/bing/v7.0/images/search"):
        super(BingImageSearch7,self).__init__(key,url)

    def search(self,query,n=10,params=None):
        params_ = {"q" : query, "count" : n }
        if params is not None:
            for k,v in params.items():
                params_[k] = v
        res = self.request_get(params=params_)
        for x in res["value"]:
            yield mdict(x)
