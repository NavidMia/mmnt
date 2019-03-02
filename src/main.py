# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

import time
import sys
import usb.core
import usb.util
import serial
from threading import Thread

import numpy as np
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from tuning import Tuning
from motor_control import MotorControl
from video_stream import VideoStream

TOP_CAM_ID = "0"
BOT_CAM_ID = "1"
TF_MODEL = "mobilenet_thin" # alternative option: "cmu"
ANGLE_THRESHOLD = 5
FACE_THRESHOLD = 50
FOV = 60
degreePerPixel = float(FOV) / float(VideoStream.DEFAULT_WIDTH)

def main():
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    time.sleep(3)
    
    mc = MotorControl()
    # mc.runMotors(90, 270)
    # sleep(2)
    # mc.runMotors(270, 90)
    # sleep(2)

    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        sys.exit("Could not find ReSpeaker Mic Array through USB")

    mic = Tuning(dev)
    mic.write("NONSTATNOISEONOFF", 1)
    mic.write("STATNOISEONOFF", 1)
    
    face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
    tfPose = TfPoseEstimator(get_graph_path(TF_MODEL), target_size=(VideoStream.DEFAULT_WIDTH, VideoStream.DEFAULT_HEIGHT))

    topCamStream = VideoStream(0)
    botCamStream = VideoStream(1)

    topCamStream.start()
    botCamStream.start()

    slaveCamID = BOT_CAM_ID
    slaveStream = botCamStream
    masterCamID = TOP_CAM_ID
    masterStream = topCamStream

    slaveTargetAngle = 0
    masterTargetAngle = 0

    updateSlaveAngle = False
    updateMasterAngle = False
    while True:
        try:
            # MASTER
            gray = cv.cvtColor(masterStream.read(), cv.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            # Focus on first face for now
            if faces:
                (x, y, w, h) = faces[0]
                midX = x + w/2
                centerDiff = abs(midX - VideoStream.DEFAULT_WIDTH/2)
                if centerDiff > FACE_THRESHOLD:
                    if midX < VideoStream.DEFAULT_WIDTH/2:
                        # rotate CCW
                        masterTargetAngle += centerDiff * degreePerPixel
                    elif midX > VideoStream.DEFAULT_WIDTH/2:
                        # rotate CW
                        masterTargetAngle -= centerDiff * degreePerPixel

                    updateMasterAngle = True

            # SLAVE
            if abs(mic.direction - slaveTargetAngle) > ANGLE_THRESHOLD
                slaveTargetAngle = mic.direction
                updateSlaveAngle = True
            # slaveImage = slaveStream.read()
            # humans = e.inference(image, resize_to_default=True, upsample_size=4.0)

            # Send Serial Commands
            if updateSlaveAngle:
                mc.runMotor(slaveCamID, slaveTargetAngle)
                updateSlaveAngle = False
            if updateMasterAngle:
                mc.runMotor(masterCamID, masterTargetAngle)
                updateMasterAngle = False
            sleep(2)

        except KeyboardInterrupt:
            print "Keyboard interrupt! Terminating."
            mc.stopMotors()
            slaveStream.stop()
            masterStream.stop()
            sleep(2)
            break

if __name__ == "__main__":
    main()
