
from PIL import Image
import numpy as np
import glob
import skimage.io as io
import tensorflow as tf
from random import shuffle
import matplotlib.pyplot as plt

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _float32_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))


dataset_squares_path = 'dataset/test/squares/*.png'
dataset_triangles_path = 'dataset/test/triangles/*.png'
tfrecords_filename = 'shape_test.tfrecords'


# read addresses and labels from the 'train' folder
squares_addrs = glob.glob(dataset_squares_path)
triangles_addrs = glob.glob(dataset_triangles_path)

squares_len = len(squares_addrs)
triangles_len = len(triangles_addrs)

# [1, 0] = squares     [0, 1] = triangles
squares_labels = np.zeros((2, squares_len), dtype=np.uint8)
squares_labels[0,:] = 1
triangles_labels = np.zeros((2, triangles_len), dtype=np.uint8)
triangles_labels[1,:] = 1

images_addrs = squares_addrs + triangles_addrs
images_labels = np.concatenate((squares_labels, triangles_labels), axis=1)

filename_pairs = list(zip(images_addrs, images_labels.T))

# to shuffle data
shuffle(filename_pairs)

# Let's collect the real images to later on compare
# to the reconstructed ones
original_images = []

writer = tf.python_io.TFRecordWriter(tfrecords_filename)

for img_path, label in filename_pairs:
    
    img = np.array(Image.open(img_path))    # (32, 32) uint8
    
    # Put in the original images into array
    # Just for future check for correctness
    original_images.append((img, label))
    img_raw = img.tostring()
    label_raw = label.tostring()
    
    example = tf.train.Example(features=tf.train.Features(feature={
        'image_raw': _bytes_feature(img_raw),
        'label_raw': _bytes_feature(label_raw),
        }))
    
    writer.write(example.SerializeToString())

writer.close()

