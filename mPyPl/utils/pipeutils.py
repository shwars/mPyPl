from pipe import *
import random, itertools
import numpy as np


# trs note -- pass l in as
# a fixed data structure i.e. array/list because (len(l)) must work
@Pipe
def pshuffle(l):
    """
    Shuffle a given pipe.
    In the current implementation, it has to store the whole datastream into memory as a list, in order to perform shuffle.
    Please not, that the idiom [1,2,3] | pshuffle() | pcycle() will return the same order of the shuffled sequence (eg. something
    like [2,1,3,2,1,3,...]), if you want proper infinite shuffle use `infshuffle()` instead.
    :param l: input pipe generator
    :return: list of elements of the datastream in a shuffled order
    """
    l = list(l)
    random.shuffle(l)
    return l

@Pipe
def pcycle(l):
    """
    Infinitely cycle the input sequence
    :param l: input pipe generator
    :return: infinite datastream
    """
    return itertools.cycle(l)

@Pipe
def infshuffle(l):
    """
    Function that turns sequence into infinite shuffled sequence. It loads it into memory for processing.
    :param l: input pipe generator
    :return: result sequence
    """
    data = list(l)
    while True:
        random.shuffle(data)
        for x in data:
            yield x

@Pipe
def as_npy(l):
    """
    Convert the sequence into numpy array. Use as `seq | as_npy`
    :param l: input pipe generator (finite)
    :return: numpy array created from the generator
    """
    return np.array(list(l))

@Pipe
def pprint(l):
    """
    Print the values of a finite pipe generator and return a new copy of it. It has to convert generator into in-memory
    list, so better not to use it with big data. Use `seq | tee ...` instead.
    :param l: input pipe generator
    :return: the same generator
    """
    l = list(l)
    print(l)
    return l


@Pipe
def first(l):
    """
    Returns first element of a pipe
    :param datastream: input pipe generator
    :return: first element
    """
    for x in l:
        return x
