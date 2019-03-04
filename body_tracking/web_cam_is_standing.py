import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

import tensorflow as tf

from tf_pose.common import CocoPart


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
    path = "is_standing_model_generation/c1200_no_bad/"
    name = "c1200_no_bad_v2"
    json_file = open(path + name + ".json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = tf.keras.models.model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(path + name + ".h5")
    print("Loaded model from disk")

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
            joint_data = []
            body_parts_not_to_add = [18, 3,4] # Dont add Background, RElbow, LElbow
            for value, body_part_name  in enumerate(CocoPart):
                if value in human.body_parts and value not in body_parts_not_to_add:
                    body_part = human.body_parts[value]
                    joint_data.append(body_part.x)
                    joint_data.append(body_part.y)
                    joint_data.append(body_part.score)
                elif value not in body_parts_not_to_add:
                    joint_data.append(-1)
                    joint_data.append(-1)
                    joint_data.append(0)
            features = tf.reshape(joint_data, shape=(1, 16*3))
            prediction = loaded_model.predict(features, steps=1)[0]
            if(prediction[0] > prediction[1]):
                cv2.putText(image,
                            "Standing",
                            (50, 50),  cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 255, 0), 2)
            else:
                cv2.putText(image,
                            "Sitting",
                            (50, 50),  cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 0, 255), 2)
            # prediction = tf.argmax(loaded_model(features), axis=1, output_type=tf.int32)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        key = cv2.waitKey(key_listener_duration)
        if key == 27: # escape key should be held
            break
        # logger.debug('finished+')

    cv2.destroyAllWindows()
