from pipe import *
import random, itertools
import numpy as np


# trs note -- pass l in as
# a fixed data structure i.e. array/list because (len(l)) must work
@Pipe
def pshuffle(l):
    random.shuffle(l)
    return l

@Pipe
def pcycle(l):
    return itertools.cycle(l)

@Pipe
def infshuffle(l):
    """
    Function that turns sequence into infinite shuffled sequence. It loads it into memory for processing.
    :param l: input sequence
    :return: result sequence
    """
    data = list(l)
    while True:
        random.shuffle(data)
        for x in data:
            yield x

@Pipe
def as_npy(l):
    return np.array(list(l))

@Pipe
def pprint(l):
    print(list(l))
    return l


@Pipe
def first(l):
    """
    Returns first element of a pipe
    :param datastream: input pipe
    :return: first element
    """
    for x in l:
        return x
