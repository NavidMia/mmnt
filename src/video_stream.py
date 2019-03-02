import cv2 as cv
import numpy as np

class VideoStream:
    DEFAULT_WIDTH = 432
    DEFAULT_HEIGHT = 368
    
    def __init__(self, camera=-1, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        if camera == -1:
            self.stream = self.open_onboard_cam(width, height)
        else:
            self.stream = cv.VideoCapture(camera)
        self.stopped = False
        (self.grabbed, self.frame) = self.stream.read()
    
    def open_onboard_cam(self, width, height):
        # On versions of L4T prior to 28.1, add 'flip-method=2' into gst_str
        gst_str = ('nvcamerasrc ! '
                   'video/x-raw(memory:NVMM), '
                   'width=(int)2592, height=(int)1458, '
                   'format=(string)I420, framerate=(fraction)30/1 ! '
                   'nvvidconv ! '
                   'video/x-raw, width=(int){}, height=(int){}, '
                   'format=(string)BGRx ! '
                   'videoconvert ! appsink').format(width, height)
        return cv.VideoCapture(gst_str, cv.CAP_GSTREAMER)

    def start(self):
        Thread(target=self.update, args=()).start()

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True