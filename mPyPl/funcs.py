# Different stream processing functions

import numpy as np

def zero_pad(x,max_frames,axis=0):
    npad = [(0, 0) for x in range(len(x.shape))]
    npad[axis] = (0, max_frames-x.shape[axis])
    return np.pad(x,npad,'constant',constant_values=0)

