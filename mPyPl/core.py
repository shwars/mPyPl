# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import os
from .mdict import *
from pipe import *
from .utils.pipeutils import *
from .utils.coreutils import *
from .utils.video import *
from .utils.fileutils import *
import builtins
import functools
import sys


# === Main pipeline operations ===

def __fextract(x,field_name):
    """
    Extract value of a given field or fields.
    :param x: mdict
    :param field_name: name of a field or list of field names
    :return: value or list of values
    """
    if field_name is None: return x
    if isinstance(field_name, list) or isinstance(field_name, np.ndarray):
        return [x[key] for key in field_name]
    else:
        return x[field_name]


def __fnapply(x,src_field,func):
    """
    Internal. Apply function `func` on the values extracted from dict `x`. If `src_fields` is string, function of one argument is expected.
    If `src_fields` is a list, `func` should take list as an argument.
    """
    return func(__fextract(x,src_field))


@Pipe
def apply(datastream, src_field, dst_field, func,eval_strategy=None):
    """
    Applies a function to the specified field of the stream and stores the result in the specified field. Sample usage:
    `[1,2,3] | as_field('f1') | apply('f1','f2',lambda x: x*x) | select_field('f2') | as_list`
    If `dst_field` is `None`, function is just executed on the source field(s), and result is not stored.
    This is useful when there are side effects.
    """
    def applier(x):
        r = (lambda : __fnapply(x,src_field,func)) if lazy_strategy(eval_strategy) else __fnapply(x,src_field,func)
        if dst_field is not None and dst_field!='':
            x[dst_field]=r
            if eval_strategy:
                x.set_eval_strategy(dst_field,eval_strategy)
        return x
    return datastream | select(applier)

@Pipe
def sapply(datastream, field, func):
    """
    Self-apply
    Applies a function to the specified field of the stream and stores the result in the same field. Sample usage:
    `[1,2,3] | as_field('x') | sapply('x',lambda x: x*x) | select_field('x') | as_list`
    """
    def applier(x):
        x[field] = func(x[field])
        return x
    return datastream | select(applier)


@Pipe
def fapply(datastream, dst_field, func, eval_strategy=None):
    """
    Applies a function to the whole dictionary and stores the result in the specified field.
    This function should rarely be used externaly, choice should be made in favour of `apply`, because it does not involve
    operating on internals of `dict`
    """
    def applier(x):
        x[dst_field] = (lambda : func(x)) if lazy_strategy(eval_strategy) else func(x)
        if eval_strategy:
            x.set_eval_strategy(dst_field,eval_strategy)
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
def apply_batch(datastream, src_field, dst_field, func, batch_size=32):
    """
    Apply function to the field in batches. `batch_size` elements are accumulated into the list, and `func` is called
    with this parameter.
    """
    n=0
    arg=[]
    seq=[]
    for x in datastream:
        if (n<batch_size):
            f = __fextract(x,src_field)
            arg.append(f)
            seq.append(x)
            n+=1
        else:
            res = func(arg)
            for u,v in zip(seq,res):
                u[dst_field] = v
                yield u
            n=0
            arg=[]
            seq=[]
    if n>0: # flush remaining items
        res = func(arg)
        for u, v in zip(seq, res):
            u[dst_field] = v
            yield u


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

@Pipe
def apply_nx(datastream, src_field, dst_field, func,eval_strategy=None,print_exceptions=False):
    """
    Same as `apply`, but ignores exceptions by just skipping elements with errors.
    """
    def applier(x):
        r = (lambda : __fnapply(x,src_field,func)) if lazy_strategy(eval_strategy) else __fnapply(x,src_field,func)
        if dst_field is not None and dst_field!='':
            x[dst_field]=r
            if eval_strategy:
                x.set_eval_strategy(dst_field,eval_strategy)
        return x
    for x in datastream:
        try:
            yield applier(x)
        except:
            if print_exceptions:
                print("[mPyPl] Exception: {}".format(sys.exc_info()))
            pass


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
    if isinstance(field_name, list) or isinstance(field_name, np.ndarray):
        for x in datastream:
            for key in field_name:
                del x[key]
            yield x  
    else:
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
def sliding_window_npy(seq,field_names,size,cache=10):
    """
    Create a stream of sliding windows from a given stream.
    :param seq: Input sequence
    :param field_names: Field names to accumulate
    :param size: Size of sliding window
    :param cache: Size of the caching array, in a number of `size`-chunks.
    :return: mPyPl sequence containing numpy arrays for specified fields
    """
    cachesize = size*cache
    buffer = None
    n = 0
    for x in seq:
        data = { i : x[i] for i in field_names }
        if n==0:
            buffer = { i : np.zeros((cachesize,)+data[i].shape) for i in field_names }
        if n<cachesize: # fill mode
            for i in field_names: buffer[i][n] = data[i]
            n+=1
        else: # spit out mode
            for i in range(cachesize-size):
                yield mdict( { j : buffer[j][i:i+size] for j in field_names })
            for i in field_names: buffer[i] = np.roll(buffer[i],(1-n)*size,axis=0)
            n=size
    # spit out the rest
    if n>size:
        for i in range(n-size):
            yield mdict( { j : buffer[j][i:i+size] for j in field_names })


@Pipe
def summarize(seq,field_name,func=None,msg=None):
    """
    Compute a summary of a given field (eg. count of different values). Resulting dictionary is either passed to `func`,
    or printed on screen (if `func is None`).
    :param seq: Datastream
    :param field_name: Field name to summarize
    :param func: Function to call after summary is obtained (which is after all stream processing). If `None`, summary is printed on screen.
    :param msg: Optional message to print before summary
    :return: Original stream
    """
    if field_name is None:
        return seq
    d = {}
    for x in seq:
        c = x.get(field_name)
        if c is not None:
            d[c] = d.get(c,0)+1
        yield x
    if func is not None:
        func(d)
    else:
        if len(d.keys())>0:
            if msg is not None: print(msg)
            for t in d.keys():
                print(" + {}: {}".format(t,d[t]))

@Pipe
def inspect(seq,func=None,message="Inspecting mdict"):
    """
    Print out the info about the fields in a given stream
    :return: Original sequence
    """
    f = True
    for x in seq:
        if f:
            f=False
            if func is not None: func(x)
            else:
                mdict.inspect(x,message=message)
        yield x


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

@Pipe
def iteri(datastream,field_name=None, func=None):
    """
    Execute function `func` on field `field_name` (or list of fields) of every item.
    If `field_name` is omitted or `None`, function is applied on the whole dictionary (this usage is not recommended).
    Function receives number of frame as the first argument
    """
    i=0
    for x in datastream:
        if func is not None:
            if field_name is None:
                func(i,x)
            else:
                __fnapply(x,field_name,functools.partial(func,i))
        yield x
        i+=1

# === Aux utility functions ===

@Pipe
def unfold(l,field_name,func,init_state):
    """
    Add extra field to the datastream, which is obtained by applying state transformation function `func` to
    initial state `init_state`
    :param l: datastream
    :param func: state transformation function
    :param init_state: initial state
    :return: datastream
    """
    s = init_state
    for x in l:
        x[field_name] = s
        s = func(s)
        yield x

@Pipe
def unroll(datastream, field):
    """
    Field `field` is assumed to be a sequence. This function unrolls the sequence, i.e. replacing the sequence field
    with the actual values inside the sequence. All other field values are duplicated.
    :param datasteam: Data stream
    :param field: Field name or list of field names. If several fields are listed, corresponding sequences should preferably be of the same size.
    """
    field = enlist(field)
    for x in datastream:
        f = __fextract(x,field)
        for v in zip(*f):
            y = mdict(x)
            for fld,val in zip(field,v): y[fld]=val
            yield y

@Pipe
def fenumerate(l,field_name,start=0):
    """
    Add extra field to datastream which contains number of record
    :param l:
    :param field_name:
    :return:
    """
    return l | unfold(field_name,init_state=start,func=lambda x: x+1)


def infinite():
    """
    Produce an infinite sequence of empty `mdict`s
    """
    while True:
        yield mdict()

@Pipe
def fold(l,field_name,func,init_state):
    """
    Perform fold of the datastream, using given fold function `func` with initial state `init_state`
    :param l: datastream
    :param field_name: field name (or list of names) to use
    :param func: fold function that takes field(s) value and state and returns state. If field_name is None, func
    accepts the whole `mdict` as first parameter
    :param init_state: initial state
    :return: final state of the fold
    """
    s = init_state
    for x in l:
        s = func(__fextract(x,field_name),s)
    return s

@Pipe
def scan(l,field_name,new_field_name,func,init_state):
    """
    Perform scan (cumulitive sum) of the datastream, using given function `func` with initial state `init_state`.
    Results are places into `new_field_name` field.
    :param l: datastream
    :param field_name: field name (or list of names) to use
    :param new_field_name: field name to use for storing results
    :param func: fold function that takes field(s) value and state and returns state. If field_name is None, func
    accepts the whole `mdict` as first parameter
    :param init_state: initial state
    :return: final state of the fold
    """
    s = init_state
    for x in l:
        s = func(__fextract(x,field_name),s)
        x[new_field_name]=s
        yield x

@Pipe
def delay(seq,field_name,delayed_field_name):
    """
    Create another field `delayed_field_name` from `field_name` that is one step delayed
    :param seq: Sequence
    :param field_name: Original existing field name
    :param delayed_field_name: New field name to hold the delayed value
    :return: New sequence
    """
    n = None
    for x in seq:
        if n is not None:
            x[delayed_field_name]=n[field_name]
            yield x
        n = x

@Pipe
def batch(datastream,k,n):
    """
    Separate only part of the stream for parallel batch processing. If you have `n` nodes, pass number of current node
    as `k` (from 0 to n-1), and it will pass only part of the stream to be processed by that node. Namely, for i-th
    element of the stream, it is passed through if i%n==k
    :param datastream: datastream
    :param k: number of current node in cluster
    :param n: total number of nodes
    :return: resulting datastream which is subset of the original one
    """
    i=0
    for x in datastream:
        if i%n==k:
            yield x
        i+=1

@Pipe
def silly_progress(seq,n=None,elements=None,symbol='.',width=40):
    """
    Print dots to indicate that something good is happening. A dot is printed every `n` items.
    :param seq: original sequence
    :param n: number of items to process between printing a dot
    :param symbol: symbol to print
    :return: original sequence
    """
    if n is None:
        n = elements//width if elements is not None else 10
    i=n
    for x in seq:
        i-=1
        yield x
        if i==0:
            print(symbol, end='')
            i=n

