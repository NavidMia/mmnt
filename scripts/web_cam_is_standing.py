import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

import tensorflow as tf

import nn_func as nn


logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0
key_listener_duration = 1
frame_count = 0


if __name__ == '__main__':
    # Load is_standing network
    nn_model = nn.get_model(path = "is_standing_model_generation/c1200_no_bad/",
                     name = "c1200_no_bad_v2")

    model = 'mobilenet_thin'
    logger.debug('initialization %s : %s' % (model, get_graph_path(model)))
    w, h = model_wh('432x368')
    # w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(model), target_size=(432, 368))
    camera_num = 0
    cam = cv2.VideoCapture(camera_num)
    # This sets the buffer size to 1
    cam.set(38, 1) # CV_CAP_PROP_BUFFERSIZE = 38

    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    resize_out_ratio = 4.0
    while True:
        print("frame " + str(frame_count))
        frame_count += 1
        ret_val, image = cam.read()
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0),
                            upsample_size=resize_out_ratio)
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        if len(humans) == 0:
            cv2.putText(image,
                        "No humans",
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 0), 2)
        elif len(humans) > 1:
            cv2.putText(image,
                        "multiple humans",
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 0), 2)
        else: # 1 human
            human = humans[0]
            if(nn.is_standing(nn_model, human)):
                cv2.putText(image,
                            "Standing",
                            (50, 50),  cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 255, 0), 2)
            else:
                cv2.putText(image,
                            "Sitting",
                            (50, 50),  cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 0, 255), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        key = cv2.waitKey(key_listener_duration)
        if key == 27: # escape key should be held
            break
        # logger.debug('finished+')

    cv2.destroyAllWindows()
