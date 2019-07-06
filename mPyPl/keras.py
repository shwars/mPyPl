# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

from pipe import Pipe
import numpy as np

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
            # explicitly compute all fields - this is needed for all fields to be computed only once for on-demand evaluation
            flds = { i : data[i] for i in (feature_field_name if isinstance(feature_field_name, list) else [feature_field_name])}
            lbls = data[label_field_name] # TODO: what happens when label_field_name is a list?
            if batch is None:
                if isinstance(feature_field_name, list):
                    batch = [np.zeros((batchsize,)+flds[i].shape) for i in feature_field_name]
                else:
                    batch = np.zeros((batchsize,)+flds[feature_field_name].shape)
                lbls_shape = lbls.shape if lbls is np.ndarray else (1,)
                labels = np.zeros((batchsize,)+lbls_shape)
            if isinstance(feature_field_name, list):
                for j,n in enumerate(feature_field_name):
                    batch[j][i] = flds[n]
            else:
                batch[i] = flds[feature_field_name]
            labels[i] = data[label_field_name]
        yield (batch, labels)
        batch = labels = None
