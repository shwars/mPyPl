# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

from pipe import Pipe

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
