import argparse
import logging
import time

import cv2
import numpy as np

fps_time = 0
key_listener_duration = 1
frame_count = 0

def open_onboard_cam(width, height):
    # On versions of L4T prior to 28.1, add 'flip-method=2' into gst_str
    gst_str = ('nvcamerasrc ! '
               'video/x-raw(memory:NVMM), '
               'width=(int)2592, height=(int)1458, '
               'format=(string)I420, framerate=(fraction)30/1 ! '
               'nvvidconv ! '
               'video/x-raw, width=(int){}, height=(int){}, '
               'format=(string)BGRx ! '
               'videoconvert ! appsink').format(width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

if __name__ == '__main__':
    cam = open_onboard_cam(432, 368)
    ret_val, image = cam.read()
    resize_out_ratio = 4.0
    while True:
        print("frame " + str(frame_count))
        frame_count += 1

        ret_val, image = cam.read()
        cv2.imshow('cv2 result', image)
        fps_time = time.time()
        key = cv2.waitKey(key_listener_duration)
        if key == 27: # escape key should be held
            break

    cv2.destroyAllWindows()

