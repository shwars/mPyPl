# This is an example of training Keras NN to classify cats and dogs
# The approach is inspired by classical article: https://blog.keras.io/building-powerful-image-classification-models-using-very-little-data.html
# Dataset should be taken from here: https://www.kaggle.com/tongpython/cat-and-dog

# This sample assumes the following directory structure under base_dir:
# - training_set
#    + cats
#    + dogs
# - test_set
#    + cats
#    + dogs

base_dir = 'e:\\data\\cat-and-dog'

import sys, os
import cv2
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('c:\work\mPyPl')

import mPyPl as mp
import mPyPl.utils.image as mpui
from mPyPl.utils.pipeutils import *
from pipe import *
import functools as fn
import keras

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

transform = keras.preprocessing.image.ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

scale_transform = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# Show first few images from the training set with transform
seq = (
    mp.get_datastream(train_dir,classes=classes,ext=".jpg")
    | pshuffle
    | take(10)
    | mp.apply('filename','image',lambda fn: mpui.im_resize(cv2.imread(fn),size=(100,100)))
    | mp.apply('image','image', transform.random_transform)
    | mp.select_field('image')
    | pexec(fn.partial(mpui.show_images,cols=2)))

# Use lazy evaluation to produce several transforms of the same image
# We will take two images, and get 5 transforms of each
(mp.get_datastream(train_dir,classes=classes,ext=".jpg")
| pshuffle
| take(2)
| mp.apply('filename','orig_image',lambda fn: cv2.imread(fn))
| mp.apply('orig_image','transformed_image', transform.random_transform, eval_strategy=mp.EvalStrategies.OnDemand)
| mp.apply('transformed_image','scaled_image', lambda x: mpui.im_resize_pad(x,size=(150,150)), eval_strategy=mp.EvalStrategies.OnDemand)
| mp.apply('scaled_image', 'image', lambda x: x/255., eval_strategy=mp.EvalStrategies.OnDemand)
| pcycle | take(10)
| mp.select_field('image')
| pexec(fn.partial(mpui.show_images,cols=2)))


# Train simple VGG network from scratch
from keras.models import Sequential
from keras.layers import *
model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(150, 150, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

no_train = 5000
no_test = 700
batch_size=16

train_seq = (
    mp.get_datastream(train_dir,classes=classes,ext=".jpg")
    | pshuffle
    | take(no_train)
    | mp.apply('filename','image',lambda fn: mpui.im_resize_pad(cv2.imread(fn),size=(150,150)))
    | mp.apply('image','ximage', transform.random_transform,eval_strategy=mp.EvalStrategies.OnDemand)
    | mp.apply('ximage', 'xximage', lambda x: x/255,eval_strategy=mp.EvalStrategies.OnDemand)
    # it is important to use OnDemand strategy here, so that new transform is re-computed on each evaluation
    # with all lazy evaluations we need to use new field names and keep the old ones for eval purposes
    | pcycle() | mp.as_batch('xximage','class_id',batchsize=batch_size))

test_seq = (
    mp.get_datastream(test_dir,classes=classes,ext=".jpg")
    | pshuffle
    | take(no_test)
    | mp.apply('filename','image',lambda fn: mpui.im_resize_pad(cv2.imread(fn),size=(150,150)))
    | mp.apply('image', 'image', lambda x: x/255)
    | mp.select_fields(['class_id','image'])
    | pcycle() | mp.as_batch(batchsize=batch_size,feature_field_name='image',label_field_name='class_id'))

hist=model.fit_generator(train_seq,steps_per_epoch=no_train//batch_size,
      validation_data=test_seq, validation_steps = no_test//batch_size,
      epochs=10)

plt.plot(hist.history['acc'])
plt.plot(hist.history['val_acc'])
plt.show()

# Transfer learning using VGG-16
from keras import applications

vgg = applications.VGG16(include_top=False,weights='imagenet',input_shape=(150,150,3))
for l in vgg.layers:
        l.trainable=False

train_seq = (
    mp.get_datastream(train_dir,classes=classes,ext=".jpg")
    | pshuffle
    | take(no_train)
    | mp.apply('filename','image',lambda fn: mpui.im_resize_pad(cv2.imread(fn),size=(150,150)))
    | mp.sapply('image', keras.applications.vgg16.preprocess_input)
    | mp.apply('image', 'vgg', lambda x: vgg.predict(np.expand_dims(x,0))[0])
    | pcycle() | mp.as_batch('vgg','class_id',batchsize=batch_size))

test_seq = (
    mp.get_datastream(test_dir,classes=classes,ext=".jpg")
    | pshuffle
    | take(no_test)
    | mp.apply('filename','image',lambda fn: mpui.im_resize_pad(cv2.imread(fn),size=(150,150)))
    | mp.sapply('image', keras.applications.vgg16.preprocess_input)
    | mp.apply('image', 'vgg', lambda x: vgg.predict(np.expand_dims(x,0))[0])
    | pcycle() | mp.as_batch(batchsize=batch_size,feature_field_name='vgg',label_field_name='class_id'))


model = Sequential()
model.add(Flatten(input_shape=(4,4,512)))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

hist=model.fit_generator(train_seq,steps_per_epoch=no_train//batch_size,
      validation_data=test_seq, validation_steps = no_test//batch_size,
      epochs=10)
