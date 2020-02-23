from __future__ import print_function
import argparse
from datetime import datetime
import time
import os
import sys
import time
import scipy.misc
import cv2
from PIL import Image

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from utils import *
from LIP_model import *

N_CLASSES = 20

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default = "../Dataset", help = "directory of data")
    parser.add_argument("--save_dir", default = "../segmentation", help = "directory of data")
    parser.add_argument("--checkpoint_dir", default = "./checkpoint/JPPNet-s2/", help = "directory of checkpoint")
    parser.add_argument("--steps", default = 15000, help = "number of images")
    parser.add_argument("--width", default = 256, help = "width size of image")
    parser.add_argument("--height", default = 256, help = "height size of image")
    args = parser.parse_args()

    """Create the model and start the evaluation process."""
    # Create queue coordinator.
    coord = tf.train.Coordinator()
    h = args.height
    w = args.width

    """Create txt file of dataset list"""
    image_list = os.listdir(args.data_dir)
    data_txt_dir = "./list/{}.txt".format(args.data_dir.split("/")[-1])
    if os.path.exists(data_txt_dir):
       data_txt_dir = data_txt_dir.split(".")[0]+"_"+".txt"
    print("text file name: {}".format(data_txt_dir))
    f = open(data_txt_dir, "w")
    for elem in image_list:
        f.write("{}\n".format(os.path.join(args.data_dir, elem)))
    f.close()

    with tf.name_scope("create_inputs"):
        reader = ImageReader(args.data_dir, data_txt_dir, None, False, False, coord)
        image = reader.image
        image_rev = tf.reverse(image, tf.stack([1]))
        image_list = reader.image_list

    image_batch_origin = tf.stack([image, image_rev])
    
    image_batch = tf.image.resize_images(image_batch_origin, [int(h), int(w)])
    image_batch075 = tf.image.resize_images(image_batch_origin, [int(h * 0.75), int(w * 0.75)])
    image_batch125 = tf.image.resize_images(image_batch_origin, [int(h * 1.25), int(w * 1.25)])

    # Create network.
    with tf.variable_scope('', reuse=False):
        net_100 = JPPNetModel({'data': image_batch}, is_training=False, n_classes=N_CLASSES)
    with tf.variable_scope('', reuse=True):
        net_075 = JPPNetModel({'data': image_batch075}, is_training=False, n_classes=N_CLASSES)
    with tf.variable_scope('', reuse=True):
        net_125 = JPPNetModel({'data': image_batch125}, is_training=False, n_classes=N_CLASSES)

    
    # parsing net
    parsing_fea1_100 = net_100.layers['res5d_branch2b_parsing']
    parsing_fea1_075 = net_075.layers['res5d_branch2b_parsing']
    parsing_fea1_125 = net_125.layers['res5d_branch2b_parsing']

    parsing_out1_100 = net_100.layers['fc1_human']
    parsing_out1_075 = net_075.layers['fc1_human']
    parsing_out1_125 = net_125.layers['fc1_human']

    # pose net
    resnet_fea_100 = net_100.layers['res4b22_relu']
    resnet_fea_075 = net_075.layers['res4b22_relu']
    resnet_fea_125 = net_125.layers['res4b22_relu']

    with tf.variable_scope('', reuse=False):
        pose_out1_100, pose_fea1_100 = pose_net(resnet_fea_100, 'fc1_pose')
        pose_out2_100, pose_fea2_100 = pose_refine(pose_out1_100, parsing_out1_100, pose_fea1_100, name='fc2_pose')
        parsing_out2_100, parsing_fea2_100 = parsing_refine(parsing_out1_100, pose_out1_100, parsing_fea1_100, name='fc2_parsing')
        parsing_out3_100, parsing_fea3_100 = parsing_refine(parsing_out2_100, pose_out2_100, parsing_fea2_100, name='fc3_parsing')

    with tf.variable_scope('', reuse=True):
        pose_out1_075, pose_fea1_075 = pose_net(resnet_fea_075, 'fc1_pose')
        pose_out2_075, pose_fea2_075 = pose_refine(pose_out1_075, parsing_out1_075, pose_fea1_075, name='fc2_pose')
        parsing_out2_075, parsing_fea2_075 = parsing_refine(parsing_out1_075, pose_out1_075, parsing_fea1_075, name='fc2_parsing')
        parsing_out3_075, parsing_fea3_075 = parsing_refine(parsing_out2_075, pose_out2_075, parsing_fea2_075, name='fc3_parsing')

    with tf.variable_scope('', reuse=True):
        pose_out1_125, pose_fea1_125 = pose_net(resnet_fea_125, 'fc1_pose')
        pose_out2_125, pose_fea2_125 = pose_refine(pose_out1_125, parsing_out1_125, pose_fea1_125, name='fc2_pose')
        parsing_out2_125, parsing_fea2_125 = parsing_refine(parsing_out1_125, pose_out1_125, parsing_fea1_125, name='fc2_parsing')
        parsing_out3_125, parsing_fea3_125 = parsing_refine(parsing_out2_125, pose_out2_125, parsing_fea2_125, name='fc3_parsing')


    parsing_out1 = tf.reduce_mean(tf.stack([tf.image.resize_images(parsing_out1_100, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out1_075, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out1_125, tf.shape(image_batch_origin)[1:3,])]), axis=0)
    parsing_out2 = tf.reduce_mean(tf.stack([tf.image.resize_images(parsing_out2_100, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out2_075, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out2_125, tf.shape(image_batch_origin)[1:3,])]), axis=0)
    parsing_out3 = tf.reduce_mean(tf.stack([tf.image.resize_images(parsing_out3_100, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out3_075, tf.shape(image_batch_origin)[1:3,]),
                                        tf.image.resize_images(parsing_out3_125, tf.shape(image_batch_origin)[1:3,])]), axis=0)

    raw_output = tf.reduce_mean(tf.stack([parsing_out1, parsing_out2, parsing_out3]), axis=0)
    head_output, tail_output = tf.unstack(raw_output, num=2, axis=0)
    tail_list = tf.unstack(tail_output, num=20, axis=2)
    tail_list_rev = [None] * 20
    for xx in range(14):
        tail_list_rev[xx] = tail_list[xx]
    tail_list_rev[14] = tail_list[15]
    tail_list_rev[15] = tail_list[14]
    tail_list_rev[16] = tail_list[17]
    tail_list_rev[17] = tail_list[16]
    tail_list_rev[18] = tail_list[19]
    tail_list_rev[19] = tail_list[18]
    tail_output_rev = tf.stack(tail_list_rev, axis=2)
    tail_output_rev = tf.reverse(tail_output_rev, tf.stack([1]))


    raw_output_all = tf.reduce_mean(tf.stack([head_output, tail_output_rev]), axis=0)
    raw_output_all = tf.expand_dims(raw_output_all, dim=0)
    raw_output_all = tf.argmax(raw_output_all, dimension=3)
    pred_all = tf.expand_dims(raw_output_all, dim=3) # Create 4-d tensor.

    # Which variables to load.
    restore_var = tf.global_variables()
    # Set up tf session and initialize variables. 
    config = tf.ConfigProto(log_device_placement=True)
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 1
    sess = tf.Session(config=config)
    init = tf.global_variables_initializer()
    
    sess.run(init)
    sess.run(tf.local_variables_initializer())
    
    # Load weights.
    loader = tf.train.Saver(var_list=restore_var)
    if args.checkpoint_dir is not None:
        if load(loader, sess, args.checkpoint_dir):
            print(" [*] Load SUCCESS")
        else:
            print(" [!] Load failed...")
    
    # Start queue threads.
    threads = tf.train.start_queue_runners(coord=coord, sess=sess)

    # Iterate over training steps.
    for step in range(args.steps):
        parsing_ = sess.run(pred_all)
        if step % 1 == 0:
            print('step {:d}'.format(step))
            print (image_list[step])
        folder_name = image_list[step].split('/')[-1]
        name = (image_list[step].split("/")[-1]).split(".")[0]
        print(name)
        
        msk = decode_labels(parsing_, num_classes=N_CLASSES)
        parsing_im_1 = Image.fromarray(msk[0])

        parsing_im_1.save('{}/{}.png'.format(args.save_dir, name))
        cv2.imwrite('{}/{}.png'.format(args.save_dir, name),parsing_[0,:,:,0])

if __name__ == "__main__":
	os.environ['CUDA_VISIBLE_DEVICES'] = "0,1,2,3"
	main()
