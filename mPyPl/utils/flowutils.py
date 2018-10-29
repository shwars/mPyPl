import cv2
import numpy as np
import os
import pickle

def load_optical(filename): 
    return pickle.load(open(filename + '.pickle', 'rb'))


def calc_gradients(flow):
    def calc(flowi):
        old, new = zip(*flowi)
        return (np.array(new) - np.array(old)).T
    return [calc(flowi) for flowi in flow if flowi]


def to_polar(video):
    return [np.array(cv2.cartToPolar(frame[0], frame[1])).squeeze(axis=2) for frame in video]


def grad_to_hist(grad, bins, lower, upper, maxv=1):
    grad[grad > upper] = upper
    grad[grad < lower] = lower
    hist, _ =  np.histogram(grad, bins=bins, range=(lower, upper))
    hist = np.log(1 + hist) / maxv
    return hist


def video_to_hist(video, params):
    hists = []
    for frame in video:
        hists.append(np.array([
            grad_to_hist(frame[0], params[0]['bins'], params[0]['lower'], params[0]['upper'], params[0]['maxv']),
            grad_to_hist(frame[1], params[1]['bins'], params[1]['lower'], params[1]['upper'], params[1]['maxv'])
        ]).T)
    return np.array(hists)


def zero_pad(matrix, shape):
    matrix = np.array(matrix)
    if len(matrix.shape) != 3 or matrix.shape > shape:
        return np.zeros(shape)
    st = shape[0] - matrix.shape[0]
    col = shape[1] - matrix.shape[1]
    zs = shape[2] - matrix.shape[2]
    return np.pad(matrix, ((0, st), (0, col), (0, zs)), 'constant', constant_values=(0))