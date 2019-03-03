# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

import time
import sys
import usb.core
import usb.util
import serial

import cv2 as cv
import numpy as np

# from tf_pose.estimator import TfPoseEstimator
# from tf_pose.networks import get_graph_path, model_wh
from tuning import Tuning
from motor_control import MotorControl
from video_stream import VideoStream

MMNT_SETUP_PRESENT = True

TOP_CAM_ID = "0"
BOT_CAM_ID = "1"
TF_MODEL = "mobilenet_thin" # alternative option: "cmu"
ANGLE_THRESHOLD = 5
FACE_THRESHOLD = 50
FOV = 60
degreePerPixel = float(FOV) / float(VideoStream.DEFAULT_WIDTH)

def main():
    print("initializing")
    if MMNT_SETUP_PRESENT:
        mc = MotorControl()
        print("initialized motor control")
        dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if not dev:
            sys.exit("Could not find ReSpeaker Mic Array through USB")
        mic = Tuning(dev)
        mic.write("NONSTATNOISEONOFF", 1)
        mic.write("STATNOISEONOFF", 1)
        print("initialized microphone")

    if MMNT_SETUP_PRESENT:
        face_cascade = cv.CascadeClassifier('/home/nvidia/mmnt/opencv/data/haarcascades_cuda/haarcascade_frontalface_default.xml')
    else:
        face_cascade = cv.CascadeClassifier('/home/nvidia/sd/opencv/data/haarcascades_cuda/haarcascade_frontalface_default.xml')
    # tfPose = TfPoseEstimator(get_graph_path(TF_MODEL), target_size=(VideoStream.DEFAULT_WIDTH, VideoStream.DEFAULT_HEIGHT))

    topCamStream = VideoStream()
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
    print("initialized video streams")

    while True:
        try:
            # MASTER
            masterFrame = masterStream.read()
            gray = cv.cvtColor(masterFrame, cv.COLOR_BGR2GRAY)
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
            slaveFrame = slaveStream.read()
            if MMNT_SETUP_PRESENT:
                if abs(mic.direction - slaveTargetAngle) > ANGLE_THRESHOLD:
                    slaveTargetAngle = mic.direction
                    updateSlaveAngle = True
                # humans = e.inference(image, resize_to_default=True, upsample_size=4.0)

            # Send Serial Commands
                if updateSlaveAngle and updateMasterAngle:
                    print("Slave Angle:", slaveTargetAngle)
                    print("Master Angle:", masterTargetAngle)
                    updateSlaveAngle = False
                    updateMasterAngle = False
                    if slaveCamID == BOT_CAM_ID:
                        mc.runMotors(masterTargetAngle, slaveTargetAngle)
                    else:
                        mc.runMotors(slaveTargetAngle, masterTargetAngle)
                elif updateSlaveAngle:
                    mc.runMotor(slaveCamID, slaveTargetAngle)
                    print("Slave Angle:", slaveTargetAngle)
                    updateSlaveAngle = False
                elif updateMasterAngle:
                    mc.runMotor(masterCamID, masterTargetAngle)
                    print("Master Angle:", masterTargetAngle)
                    updateMasterAngle = False

            # 1) Sleep if not showing frames
            time.sleep(2)

            # OR 2) Display debug frames
            # cv.imshow('Master Camera', masterFrame)
            # cv.imshow('Slave Camera', slaveFrame)
            # if cv.waitKey(1) == 27:
            #     pass

        except KeyboardInterrupt:
            print("Keyboard interrupt! Terminating.")
            if MMNT_SETUP_PRESENT:
                mc.stopMotors()
            slaveStream.stop()
            masterStream.stop()
            time.sleep(2)
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
