from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import tensorflow as tf
import sys,os
sys.path.append(os.path.dirname('models/slim/'))
from nets import nets_factory
from preprocessing import preprocessing_factory
from urllib2 import urlopen
import numpy as np
import imghdr

def get_image_data(url=None, img_path=None):
  raw_image = None
  if url != None:
    raw_image = urlopen(url).read()
  elif img_path != None:
    raw_image = tf.read_file(img_path)
    with open(img_path, 'rb') as fp:
      imagedata = fp.read()
    imagetype = imghdr.what(None, h=imagedata)
    if imagetype in ["jpg","jpeg"]:
      return tf.image.decode_jpeg(raw_image, channels=3)
    if imagetype in ["png"]:
      return tf.image.decode_png(raw_image, channels=3) 
  return tf.image.decode_image(raw_image, channels=3)
    
slim = tf.contrib.slim

def result(checkpoint_path=None, model_name=None, num_classes=0, img_path=None):
  with tf.Graph().as_default():
    tf_global_step = slim.get_or_create_global_step()
    
    ####################
    # Select the model #
    ####################
    network_fn = nets_factory.get_network_fn(
        model_name,
        num_classes=(num_classes - 0),
        is_training=False)
    
    #####################################
    # Select the preprocessing function #
    #####################################
    preprocessing_name = model_name
    image_preprocessing_fn = preprocessing_factory.get_preprocessing(
        preprocessing_name,
        is_training=False)

    eval_image_size = network_fn.default_image_size
    sample_image = get_image_data(img_path=img_path)
    image = image_preprocessing_fn(sample_image, eval_image_size, eval_image_size)
    image  = tf.expand_dims(image, 0)

    logits,end_points = network_fn(image)
    predictions = tf.argmax(logits, 1)
    probabilities = tf.nn.softmax(logits)

    ####################
    # Print Probability #
    ####################

    config = tf.ConfigProto(
        device_count = {'GPU': 0}
    )

    with tf.Session(config=config) as sess:
        saver = tf.train.Saver()
        saver.restore(sess, checkpoint_path)
        proba = sess.run(probabilities)[0]
        result = np.array([[i, p] for i, p in zip(range(num_classes), proba)])
    print(np.argsort(result,axis=0)[::-1][0,1])

    return result