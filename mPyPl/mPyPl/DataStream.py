# Libary for working with data streams
from typing import TypeVar, Iterable, Tuple, Union
import os
from .LazyDict import *
from pipe import *
from .utils.pipeutils import *
from .utils.video import *
import utils.fileutils as fu
import builtins
import functools

def get_filestream(data_dir: str, ext: str) -> Iterable[str]:
    """
    Get a list of files from the given directory with specified extension  }
    :rtype: Iterable[str]
    """
    return os.listdir(data_dir) \
        | where(lambda p: p.endswith(ext)) \
        | select( lambda p: os.path.join(data_dir,p))


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
    Applies a function to the specified field of the stream and stores the result in the specified field
    """
    def applier(x):
        x[dst_field] = __fnapply(x,src_field,func)
        return x
    return datastream | select(applier)

@Pipe
def fapply(datastream, dst_field, func):
    """
    Applies a function to the whole dictionary and stores the result in the specified field.
    This function should rarely be used externaly, choice should be made in favour of `apply`
    """
    def applier(x):
        x[dst_field] = func(x)
        return x
    return datastream | select(applier)


@Pipe
def lzapply(datastream, src_field, dst_field, func):
    """
    Lazily applies a function to the specified field of the stream and stores the result in the specified field.
    You need to make sure that `lzapply` does not create endless recursive loop - you should not use the same
    `src_field` and `dst_field`, and avoid situations when x['f1'] lazily depends on x['f2'], while x['f2'] lazily
    depends on x['f1'].
    """
    def applier(x):
        x[dst_field] = lambda: __fnapply(x,src_field,func)
        return x
    return datastream | select(applier)

def count_classes(datastream):
    """
    Count number of samples in different classes in dataset
    :param datastream: input datastream
    :return: dictionary of the form { 'class_name' : no_of_elements, ... }
    """
    dic = {}
    for x in datastream:
        if x["class_name"] in dic:
            dic[x["class_name"]] += 1
        else:
            dic[x["class_name"]] = 1
    return dic


def make_split(datastream,split=0.2):
    cls = count_classes(datastream)
    mx = builtins.min(cls.values())
    n = int(mx*split)
    res = list(cls.keys()) | select (lambda c : datastream | where (lambda x: x["class_name"]==c) | as_list | pshuffle | take(n)) | chain
    return res | select(lambda x: os.path.basename(x["filename"])) | as_list

@Pipe
def datasplit(datastream,split_filename,split=0.2):
    if os.path.isfile(split_filename):
        test_list = fu.readlines(split_filename)
    else:
        datastream = list(datastream) # need to cache datastream if split does not exist
        test_list = make_split(datastream, split=split)
        fu.writelines(split_filename, test_list)
    return datastream | apply('filename', 'split', lambda x : 'V' if os.path.basename(x) in test_list else 'T')
#TODO: Handle train-validation-test split when tuple is passed in the form split=(Train,Valid,Test)

def get_datastream(data_dir, ext, classes, split_filename=None):
    """
    Get a stream of objects for a number of classes specified as dict of the form { 'dir0' : 0, 'dir1' : 1, ... }
    Returns stream of dictionaries of the form { class_id: ... , class_name: ..., filename: ... }
    """
    stream = list(classes.items()) \
            | select(lambda kv: get_filestream(os.path.join(data_dir,kv[0]),ext)\
            | select(lambda x: LazyDict({ "filename": x, "class_id": kv[1], "class_name": kv[0] }))) \
            | chain
    if split_filename:
        return stream | datasplit(os.path.join(data_dir,split_filename))
    else:
        return stream

@Pipe
def filtersplit(datastream,split_kind):
    return datastream | where(lambda x: x['split']==split_kind)

@Pipe
def make_train_test_split(datastream):
    res = { 'T': [], 'V': [] }
    for x in datastream:
        res[x['split']].append(x)
    return res['T'],res['V']

def load_video(video, video_size=(100,100), squarecrop=False, fps=25, maxlength=5, use_cache=False):
    """
    Adorn video content
    """
    return video_to_npy(
        video,
        width=video_size[0],
        height=video_size[1],
        squarecrop=squarecrop,
        fps=fps,
        maxlength=maxlength,
        use_cache=use_cache
    )


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
def delfield(datastream,field_name):
    """
    Delete specified field `field_name` from the stream. This is typically done in order to save memory.
    """
    for x in datastream:
        del x[field_name]
        yield x

@Pipe
def to_field(datastream,field_name):
    """
    Convert stream of any objects into proper datastream, with one named field
    """
    return datastream | select( lambda x : LazyDict( { field_name : x}))

@Pipe
def extract_field(datastream,field_name):
    """
    Extract one field from datastream, returning a stream of objects of corresponding type.
    """
    return datastream | select(lambda x: x[field_name])

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
def as_batch(flow, feature_field_name='features', label_field_name='label', batchsize=16):
    """
    Split input datastream into a sequence of batches suitable for keras training.
    :param flow: input datastream
    :param feature_field_name: feature field name to use. can be string or list of strings (for multiple arguments). Defaults to `features`
    :param label_field_name: Label field name. Defaults to `label`
    :param batchsize: batch size. Defaults to 16.
    :return: sequence of batches that can be passed to `flow_generator` or similar function in keras
    """
    #TODO: Test this function on multiple inputs!
    batch = labels = None
    while (True):
        for i in range(batchsize):
            data = next(flow)
            if batch is None:
                if isinstance(feature_field_name, list):
                    batch = [np.zeros((batchsize,)+data[i].shape) for i in feature_field_name]
                else:
                    batch = np.zeros((batchsize,)+data[feature_field_name].shape)
                labels = np.zeros((batchsize,1))
            if isinstance(feature_field_name, list):
                for j,n in enumerate(feature_field_name):
                    batch[j][i] = data[n]
            else:
                batch[i] = data[feature_field_name]
            labels[i] = data[label_field_name]
        yield (batch, labels)
        batch = labels = None
