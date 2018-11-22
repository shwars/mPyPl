# This is an example of training Keras NN to classify cats and dogs
# Dataset should be taken from here: https://www.kaggle.com/tongpython/cat-and-dog

# This sample assumes the following directory structure under base_dir:
# - training_set
#    + cats
#    + dogs
# - test_set
#    + cats
#    + dogs

base_dir = 'z:\\data\\cats-n-dogs'

import sys, os
import cv2
import keras as K

sys.path.append('z:\GitWork\mPyPl')

import mPyPl as mp
import mPyPl.utils.image as mpui
from mPyPl.utils.pipeutils import *
from pipe import *
import functools as fn

print(mp.__version__)

train_dir = os.path.join(base_dir,'training_set')
test_dir = os.path.join(base_dir,'test_set')

classes = mp.get_classes(train_dir)
# we need to explicitly get classes in order to have the same correspondence of class and int for train and test set

# Show first few images from the training set
seq = (
    mp.get_datastream(train_dir,classes=classes)
    | take(10)
    | mp.apply('filename','image',lambda fn: mpui.im_resize_pad(cv2.imread(fn),size=(100,100)))
    | mp.select_field('image')
    | pexec(fn.partial(mpui.show_images,cols=2)))

transform = K.preprocessing.image.ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

