# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

"""
This module expects the following directory structure of files:
```
   base_dir
        class_1
           file1.ext
           file2.ext
           ...
        class_2
           file_1.ext
           ...
        split.txt - splitter file to define train-test split of files (contains filenames)
"""

import enum
from pipe import *
from .core import *
from .utils.fileutils import *

SplitType = enum.Enum('SplitType',['Unknown','Train','Test','Valiadation'])

@Pipe
def datasplit(datastream,split_param=None,split_value=0.2):
    """
    Very flexible function for splitting the dataset into train-test or train-test-validation dataset. If datastream
    contains field `filename` - all splitting is performed based on the filename (directories are ommited to simplify
    moving data and split file onto different path). If not - original objects are used.
    :param datastream: datastream to split
    :param split_param: either filename of 'split.txt' file, or dictionary of filenames. If the file does not exist - stratified split is performed, and file is created. If `split_param` is None, temporary split is performed.
    :param split_value: either one value (default is 0.2), in which case train-test split is performed, or pair of `(validation,test)` values
    :return: datastream with additional field `split`
    """
    def mktype(x):
        t = os.path.basename(x['filename']) if 'filename' in x.keys() else x
        if t in dict['Test']:
            return SplitType.Test
        elif t in dict['Train']:
            return SplitType.Train
        elif 'Validation' in dict.keys() and t in dict['Validation']:
            return SplitType.Validation
        else:
            return SplitType.Unknown

    dict = None
    if isinstance(split_param,builtins.dict):
        dict = split_param
    elif isinstance(split_param,str):
        if os.path.isfile(split_param):
            dict = read_dict_text(split_param)
    elif split_param:
        raise("Wrong type of split_param")
    else:
        pass

    if not dict:
        datastream = list(datastream)
        dict = make_split(datastream,split_value)
        if isinstance(split_param,str):
            write_dict_text(split_param,dict)

    return datastream | fapply('split', mktype)


def make_split(datastream,split_value=0.2):
    """
    Split datastream into train-validation-test or train-test sets in a stratified manner.
    :param datastream: datastream to use
    :param split_value: if float - indicates fraction of data to be used for test dataset. If typle `(val,test)` - indicates
    fractions used for validation and test split accordingly. Detaults to 0.2.
    :return: Dictionary with objects split between given datasets. If datastream contains `filename` field, filenames are returned,
    otherwise the actual objects.
    """
    multisplit = isinstance(split_value,tuple)
    cls = datastream | dict_group_by('class_id')
    if multisplit:
        dict = { 'Train': [], 'Test': [], 'Validation': []}
    else:
        dict = { 'Train': [], 'Test': []}
    for k,v in cls.items():
        random.shuffle(v)
        if 'filename' in v[0].keys():
            v = [os.path.basename(x['filename']) for x in v]
        l = len(v)
        if multisplit:
            n1 = int(split_value[0]*l)
            n2 = n1+int(split_value[1]*l)
            dict['Test'].extend(v[:n1])
            dict['Validation'].extend(v[n1:n2])
            dict['Train'].extend(v[n2:])
        else:
            n = int(split_value*l)
            dict['Test'].extend(v[:n])
            dict['Train'].extend(v[n:])
    return dict


def get_datastream(data_dir, ext, classes, split_filename=None):
    """
    Get a stream of objects for a number of classes specified as dict of the form { 'dir0' : 0, 'dir1' : 1, ... }
    Returns stream of dictionaries of the form { class_id: ... , class_name: ..., filename: ... }
    `classes` is the dictionary of the form { 'class_name' : class_id, ... }
    """
    stream = list(classes.items()) \
            | select(lambda kv: get_filestream(os.path.join(data_dir,kv[0]),ext)\
            | select(lambda x: mdict({ "filename": x, "class_id": kv[1], "class_name": kv[0] }))) \
            | chain
    if split_filename:
        return stream | datasplit(os.path.join(data_dir,split_filename))
    else:
        return stream

@Pipe
def sample_classes(datastream,class_field_name,n=10,classes=None):
    """
    Create a datastream containing at most `n` samples from each of the classes defined by `class_field_name`
    **Important** If `classes` is `None`, function determines classes on the fly, in which case it is possible that it will terminate early without
    giving elements of all classes.
    :param datastream: input stream
    :param class_field_name: name of the field in the stream speficying the class
    :param n: number of elements of each class to take
    :param classes: classes descriptor, either dictionary or list
    :return: resulting stream
    """
    if classes is not None:
        if isinstance(classes,dict):
            classes = classes.keys()
        dic = { x : n for x in classes }
    else:
        dic = {}
    for x in datastream:
        v = x[class_field_name]
        if v in dic.keys():
            if dic[v]>0:
                dic[v] -= 1
                yield x
        else:
            dic[v] = n-1
            yield x
        if sum(dic.values())==0:
            return

@Pipe
def count_classes(datastream,class_field_name):
    """
    Count number of elements in difference classes.
    :param datastream: input data stream
    :param class_field_name: name of the field to be used for counting
    :return: mdict with classes and their values
    """
    m = mdict()
    for x in datastream:
        if x[class_field_name] in m.keys():
            m[x[class_field_name]] += 1
        else:
            m[x[class_field_name]] = 1
    return m

@Pipe
def filter_split(datastream,split_type):
    """
    Returns a datastream of the corresponding split type
    :param datastream: Input datastream
    :return: Tuple of the form `(train_stream,test_stream)`
    """
    return datastream | where(lambda x: x['split']==split_type)

@Pipe
def make_train_test_split(datastream):
    """
    Returns a tuple of streams with train and test dataset. It can be used in the following manner:
    `train, test = get_datastream(..) | ... | make_train_test_split()`
    **Important**: this causes the whole dataset to be loaded into memory. If objects are large, you are encouraged
    to use lazy field evaluation, or to handle it using the following way:
    ```
    train = get_datastream('...') | ... | filter_split(SplitType.Train)
    test = get_datastream('...') | ... | filter_split(SplitType.Test)
    ```
    :param datastream: Input datastream
    :return: Tuple of the form `(train_stream,test_stream)`
    """
    datastream = list(datastream)
    return (
        datastream | where (lambda x: x['split'] == SplitType.Train),
        datastream | where(lambda x: x['split'] == SplitType.Test)
    )

@Pipe
def make_train_validation_test_split(datastream):
    """
    Returns a tuple of streams with train, validation and test dataset. See `make_train_test_split` documentation for
    limitations and usage suggestions.
    :param datastream: Input datastream
    :return: Tuple of the form `(train_stream,validation_stream,test_stream)`
    """
    datastream = list(datastream)
    return (
        datastream | where(lambda x: x['split'] == SplitType.Train),
        datastream | where(lambda x: x['split'] == SplitType.Validation),
        datastream | where(lambda x: x['split'] == SplitType.Test)
    )