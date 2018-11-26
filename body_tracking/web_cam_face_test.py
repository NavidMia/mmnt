import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

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
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    # parser.add_argument('--camera', type=int, default=0)

    # parser.add_argument('--resize', type=str, default='0x0',
    #                     help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    # parser.add_argument('--resize-out-ratio', type=float, default=4.0,
    #                     help='if provided, resize heatmaps before they are post-processed. default=1.0')

    # parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    # parser.add_argument('--show-process', type=bool, default=False,
    #                     help='for debug purpose, if enabled, speed for inference is dropped.')
    parser.add_argument('--d', nargs='?')
    args = parser.parse_args()

    # logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    model = 'mobilenet_thin'
    logger.debug('initialization %s : %s' % (model, get_graph_path(model)))
    w, h = model_wh('432x368')
    # w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(model), target_size=(432, 368))
    # logger.debug('cam read+')
    camera_num = 0
    cam = cv2.VideoCapture(camera_num)
    # cam = cv2.VideoCapture(args.camera)

    if args.d:
        key_listener_duration = 30

    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    resize_out_ratio = 4.0
    while True:
        print("frame " + str(frame_count))
        frame_count += 1

        ret_val, image = cam.read()
        # logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=resize_out_ratio)

        move = -10
        if len(humans) > 0:
            human = humans[0]
            face = human.get_face_box(w, h)
            if face != None:
                # print(len(humans), face["x"]) # debug, need to verify face box works (Alex)
                move = (2.0*face["x"]/w - 1.0)

        # logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        # logger.debug('show+')
        if (move > 0.3333333):
            cv2.putText(image,
                        "Person is right of center",
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 0), 2)
        elif (move > -0.3333333):
            cv2.putText(image,
                        "Person is centered",
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
        elif (move > -1):
            cv2.putText(image,
                        "Person is left of center",
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 255), 2)


        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        key = cv2.waitKey(key_listener_duration)
        if key == 27: # escape key should be held
            break
        # logger.debug('finished+')

    cv2.destroyAllWindows()
