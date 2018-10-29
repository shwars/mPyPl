# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import enum

"""
Different evaluation strategies that can be used for `mdict` slots:
  * `Value` - just the value stored as in normal dictionary
  * `LazyMemoized` - a function is stored, which is evaluated upon calling the field with `x[...]`. Result is stored back into the field, so that in is not re-computed again. 
  * `OnDemand` - similar to `LazyMemoized`, but the result is not stored, and function is called each time to get the value. This is very useful for large video objects not to persist in memory.
"""
EvalStrategies = enum.Enum('EvalStrategies','Default Value LazyMemoized OnDemand')


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
            res = res.__call__()
            if self.eval_strategies.get(item,EvalStrategies.LazyMemoized) == EvalStrategies.LazyMemoized:
                res[item] = res
        return res

    def get(self, item, default=None):
        return dict.__getitem__(self,item,default)
