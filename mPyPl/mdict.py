# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import enum
from .utils.coreutils import getattritem
import json
import numpy as np

"""
Different evaluation strategies that can be used for `mdict` slots:
  * `Value` - just the value stored as in normal dictionary
  * `LazyMemoized` - a function is stored, which is evaluated upon calling the field with `x[...]`. Result is stored back into the field, so that in is not re-computed again. 
  * `OnDemand` - similar to `LazyMemoized`, but the result is not stored, and function is called each time to get the value. This is very useful for large video objects not to persist in memory.
"""
EvalStrategies = enum.Enum('EvalStrategies','Default Value LazyMemoized OnDemand')

def lazy_strategy(eval_strategy):
    """
    Determines if a given eval strategy is lazy (`LazyMemoized` or `OnDemand`)
    :param eval_strategy: input evaluation strategy
    :return: True, if eval_strategy is lazy
    """
    return eval_strategy==EvalStrategies.LazyMemoized or eval_strategy==EvalStrategies.OnDemand

class mdict(dict):
    """
    Base Dictionary class that flows through the pipeline. It supports different evaluation strategies, including
    lazy evaluation with or without memoization.
    """
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.eval_strategies = {}

    def set(self,key,value,eval_strategy=None):
        """
        Set the value of a slot and optionally its evaluation strategy
        """
        dict.__setitem__(key,value)
        self.set_eval_strategy(key,eval_strategy)


    def set_eval_strategy(self,key,eval_strategy):
        if eval_strategy is not None:
            self.eval_strategies[key] = eval_strategy


    def __getitem__(self, item):
        res = dict.__getitem__(self,item)
        if callable(res) and self.eval_strategies.get(item,EvalStrategies.Default) != EvalStrategies.Value:
            r = res.__call__()
            if self.eval_strategies.get(item,EvalStrategies.LazyMemoized) == EvalStrategies.LazyMemoized:
                self[item] = r
            return r
        else:
            return res

    def get(self, item, default=None):
        return dict.get(self,item,default)

    def as_float(self,item):
        return float(self[item])

    def as_int(self,item):
        return int(self[item])

    def as_csv(self):
        return ','.join(map(encode_csv,self.values()))

    def as_csv_header(self):
        return ','.join(map(encode_csv,self.keys()))

    def clone(self,fields=None):
        if fields is None:
            d = mdict(self)
        else:
            d = mdict({k: self[k] for k in fields})
        d.eval_strategies = self.eval_strategies
        return d

    @staticmethod
    def extract_from_object(x,fields):
        """
        Create new `mdict`, extracting specified fields from a given object or dictionary
        :param x: Object to use
        :param fields: List of fields to extract. If a field contains `.`, complex extraction is performed.
        :return: new `mdict` containing all specified fields
        """
        m = mdict()
        for z in fields:
            m[z] = getattritem(x,z)
        return m

    @staticmethod
    def to_mdict(x,include_fields=None,exclude_fields=None):
        """
        Convert an arbitrary dictionary to `mdict`
        :param x: A dictionary
        :return: `mdict` object with the same fields
        """
        m = mdict()
        kz = x.keys() if include_fields is None else include_fields
        for z in kz:
            if exclude_fields is None or z not in exclude_fields:
                m[z] = x[z]
        return m

    @staticmethod
    def from_json(fn):
        with open(fn, 'r') as f:
            res = json.load(f)
        for x in res:
            yield mdict.to_mdict(x)

    @staticmethod
    def inspect(md, message="Inspecting mdict"):
        flds = md.keys()
        print(message)
        for x in flds:
            add = ""
            t = md.get(x, None)
            if t is not None:
                add = ", type={}".format(type(t))
                if type(t) is np.ndarray:
                    add += ", shape={}".format(t.shape)
            print(" + {}, eval strategy={}{}".format(x, md.eval_strategies.get(x, None), add))  # TODO: print eval options and type
