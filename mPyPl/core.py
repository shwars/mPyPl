# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import os
from .mdict import *
from pipe import *
from .utils.pipeutils import *
from .utils.video import *
from .utils.fileutils import *
import builtins
import functools


# === Main pipeline operations ===

def __fnapply(x,src_field,func):
    """
    Internal. Apply function `func` on the values extracted from dict `x`. If `src_fields` is string, function of one argument is expected.
    If `src_fields` is a list, `func` should take list as an argument.
    """
    if isinstance(src_field, list) or isinstance(src_field, np.ndarray):
        return func([x[key] for key in src_field])
    else:
        return func(x[src_field])


@Pipe
def apply(datastream, src_field, dst_field, func):
    """
    Applies a function to the specified field of the stream and stores the result in the specified field. Sample usage:
    `[1,2,3] | as_field('f1') | apply('f1','f2',lambda x: x*x) | select_field('f2') | as_list`
    """
    def applier(x):
        x[dst_field] = __fnapply(x,src_field,func)
        return x
    return datastream | select(applier)

@Pipe
def fapply(datastream, dst_field, func):
    """
    Applies a function to the whole dictionary and stores the result in the specified field.
    This function should rarely be used externaly, choice should be made in favour of `apply`, because it does not involve
    operating on internals of `dict`
    """
    def applier(x):
        x[dst_field] = func(x)
        return x
    return datastream | select(applier)


@Pipe
def lzapply(datastream, src_field, dst_field, func, eval_strategy = None):
    """
    Lazily applies a function to the specified field of the stream and stores the result in the specified field.
    You need to make sure that `lzapply` does not create endless recursive loop - you should not use the same
    `src_field` and `dst_field`, and avoid situations when x['f1'] lazily depends on x['f2'], while x['f2'] lazily
    depends on x['f1'].
    """
    def applier(x):
        x[dst_field] = lambda: __fnapply(x,src_field,func)
        x.set_eval_strategy(dst_field,eval_strategy)
        return x
    return datastream | select(applier)

@Pipe
def apply_npy(datastream,src_field, dst_field, func, file_ext=None):
    """
    A caching apply that computes some function returning numpy array, and stores the result on disk
    :param datastream: datastream
    :param src_field: source field to use as argument. Can be one field or list of fields
    :param dst_field: destination field name
    :param func: function to apply, accepts either one argument or list of arguments
    :param file_ext: file extension to use (dst_field+'.npy') by default
    :return: processed file stream
    """
    def applier(x,file_ext):
        fn = x['filename'] + file_ext
        if os.path.isfile(fn):
            return np.load(fn)
        else:
            res = __fnapply(x,src_field,func)
            np.save(fn,res)
            return res
    if not file_ext:
        file_ext = dst_field + ".npy"
    return datastream | fapply(dst_field, functools.partial(applier,file_ext=file_ext))


# ==== Filter =====

@Pipe
def filter(datastream, src_field, pred):
    """
    Filters out fields that yield a given criteria.
    :param datastream: input datastream
    :param src_field: field of list of fields to consider
    :param pred: predicate function. If `src_field` is one field, than `pred` is a function of one argument returning boolean.
    If `src_field` is a list, `pred` takes tuple/list as an argument.
    :return: datastream with fields that yield predicate
    """
    def filtr(x):
        return __fnapply(x,src_field,pred)
    return datastream | where(filtr)


# === Field manipulations ===

@Pipe
def delfield(datastream,field_name):
    """
    Delete specified field `field_name` from the stream. This is typically done in order to save memory.
    """
    for x in datastream:
        del x[field_name]
        yield x

@Pipe
def as_field(datastream,field_name):
    """
    Convert stream of any objects into proper datastream of `mdict`'s, with one named field
    """
    return datastream | select( lambda x : mdict( { field_name : x}))

@Pipe
def ensure_field(datastream,field_name):
    """
    Ensure that the field with the given name exists. All records non containing that field are skipped.
    :param datastream: input datastream
    :param field_name: field name
    :return: output datastream
    """
    return datastream | where(lambda x: field_name in x.keys())

@Pipe
def select_field(datastream,field_name):
    """
    Extract one/several fields from datastream, returning a stream of objects of corresponding type (not `mdict`).
    If several fields are given, return a list/tuple.
    """
    return datastream | select(functools.partial(__fnapply, src_field=field_name, func=lambda x: x))

@Pipe
def select_fields(datastream,field_names):
    """
    Select multiple fields from datastream, returning a *new* stream of *mdicts* with the requested fields copied.
    Because field immutability is encouraged, the best way to get rid of some fields and free up memory
    is to select out a new data structure with the ones you want copied over.
    """
    return datastream | select(lambda x: mdict({k: x[k] for k in field_names}))

@Pipe
def dict_group_by(datasteam, field_name):
    """
    Group all the records by the given field name. Returns dictionary that for each value of the field contains lists
    of corresponding `mdict`-s. **Important**: This operation loads whole dataset into memory, so for big data fields
    it is better to use lazy evaluation.
    :param datasteam: input datastream
    :param field_name: field name to use
    :return: dictionary of the form `{ 'value-1' : [ ... ], ...}`
    """
    dict = {}
    for x in datasteam:
        if x[field_name] in dict.keys():
            dict[x[field_name]].append(x)
        else:
            dict[x[field_name]] = [x]
    return dict

@Pipe
def iter(datastream,field_name=None, func=None):
    """
    Execute function `func` on field `field_name` (or list of fields) of every item.
    If `field_name` is omitted or `None`, function is applied on the whole dictionary (this usage is not recommended).
    """
    for x in datastream:
        if func is not None:
            if field_name is None:
                func(x)
            else:
                __fnapply(x,field_name,func)
        yield x

