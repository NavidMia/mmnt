# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

import time
import sys
import usb.core
import usb.util
import serial
import logging

import cv2 as cv
import numpy as np
import human_tracking as ht

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from tf_pose.common import CocoPart

from tuning import Tuning
from motor_control import MotorControl
from video_stream import VideoStream

DISPLAY_VIDEO = False

RESIZE_RATIO = 4.0
BOT_CAM_ID = "0"
TOP_CAM_ID = "1"
TF_MODEL = "mobilenet_thin" # alternative option: "cmu"
ANGLE_THRESHOLD = 5
FACE_THRESHOLD = float(VideoStream.DEFAULT_WIDTH) / 3.0 / 2.0 + 40
FOV = 60

MASTER_SAMPLE_FREQ = 2.5
SLAVE_SAMPLE_FREQ = 0.1
SLAVE_MASTER_THRESHOLD = 45

degreePerPixel = float(FOV) / float(VideoStream.DEFAULT_WIDTH)

headParts = [CocoPart.Nose.value,
             CocoPart.REye.value,
             CocoPart.LEye.value,
             CocoPart.REar.value,
             CocoPart.LEar.value,
             CocoPart.Neck.value]

def main():
    logging.basicConfig()
    logger = logging.getLogger("MMNT")
    logger.setLevel(logging.INFO)
    logger.info("Initializing")

    masterSampleTime = time.time()
    slaveSampleTime = time.time()

    logger.debug("Initializing motor control")
    mc = MotorControl()
    mc.resetMotors()
    logger.debug("Initializing microphone")
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        sys.exit("Could not find ReSpeaker Mic Array through USB")
    mic = Tuning(dev)
    mic.write("NONSTATNOISEONOFF", 1)
    mic.write("STATNOISEONOFF", 1)

    logger.debug("Initializing models")
    ht_model = ht.get_model()
    tfPose = TfPoseEstimator(get_graph_path(TF_MODEL), target_size=(VideoStream.DEFAULT_WIDTH, VideoStream.DEFAULT_HEIGHT))

    logger.debug("Initializing video streams")
    topCamStream = VideoStream(1)
    botCamStream = VideoStream(2)

    topCamStream.start()
    botCamStream.start()


    masterCamID = TOP_CAM_ID
    masterStream = topCamStream
    slaveCamID = BOT_CAM_ID
    slaveStream = botCamStream

    masterTargetAngle = 0
    slaveTargetAngle = 180

    updateMasterAngle = False
    updateSlaveAngle = False

    masterTracking = False

    logger.info("Initialization complete")
    while True:
        try:
            # MASTER
            masterFrame = masterStream.read()
            if time.time() - masterSampleTime > MASTER_SAMPLE_FREQ:
                humans = tfPose.inference(masterFrame, resize_to_default=True, upsample_size=RESIZE_RATIO)
                if len(humans):
                    logger.debug("Master tracking")
                    masterTracking = True
                    if DISPLAY_VIDEO:
                        TfPoseEstimator.draw_humans(masterFrame, humans, imgcopy=False)
                    human = humans[0]
                    if (ht.is_hands_above_head(human)):
                        logger.debug("HANDS ABOVE HEAD!!!")
                    midX = -1
                    for part in headParts:
                        if part in human.body_parts:
                            midX = human.body_parts[part].x * VideoStream.DEFAULT_WIDTH
                            break
                    if midX != -1:
                        centerDiff = abs(midX - VideoStream.DEFAULT_WIDTH/2)
                        if centerDiff > FACE_THRESHOLD:
                            if midX < VideoStream.DEFAULT_WIDTH/2:
                                # rotate CCW
                                masterTargetAngle += centerDiff * degreePerPixel
                            elif midX > VideoStream.DEFAULT_WIDTH/2:
                                # rotate CW
                                masterTargetAngle -= centerDiff * degreePerPixel

                            masterTargetAngle = masterTargetAngle % 360
                            updateMasterAngle = True
                            masterSampleTime = time.time()
                else:
                    logger.debug("Master stopped tracking")
                    masterTracking = False

                # If master is not tracking a human, move towards speech
                if not masterTracking:
                    speechDetected, micDOA = mic.speech_detected(), mic.direction
                    logger.debug("master speech detected:", speechDetected, "diff:", abs(micDOA - masterTargetAngle))
                    if speechDetected and abs(micDOA - masterTargetAngle) > ANGLE_THRESHOLD:
                        masterTargetAngle = micDOA
                        logger.debug("Update master angle:", masterTargetAngle)
                        masterSampleTime = time.time()
                        updateMasterAngle = True

            # SLAVE
            slaveFrame = slaveStream.read()
            if time.time() - slaveSampleTime > SLAVE_SAMPLE_FREQ:
                # If master is not tracking a human and a slave sees a human, move master to the visible human and move slave away
                if not masterTracking and time.time() - masterSampleTime > MASTER_SAMPLE_FREQ:
                    humans = tfPose.inference(slaveFrame, resize_to_default=True, upsample_size=RESIZE_RATIO)
                    if len(humans):
                        logger.debug("slave found mans")
                        if DISPLAY_VIDEO:
                            TfPoseEstimator.draw_humans(slaveFrame, humans, imgcopy=False)
                        human = humans[0]
                        if (ht.is_hands_above_head(human)):
                            logger.debug("HANDS ABOVE HEAD!!!")
                        midX = -1
                        for part in headParts:
                            if part in human.body_parts:
                                midX = human.body_parts[part].x * VideoStream.DEFAULT_WIDTH
                                break
                        if midX != -1:
                            centerDiff = abs(midX - VideoStream.DEFAULT_WIDTH/2)
                            # if centerDiff > FACE_THRESHOLD:
                            if midX < VideoStream.DEFAULT_WIDTH/2:
                                # rotate CCW
                                masterTargetAngle = slaveTargetAngle + centerDiff * degreePerPixel
                            elif midX > VideoStream.DEFAULT_WIDTH/2:
                                # rotate CW
                                masterTargetAngle = slaveTargetAngle - centerDiff * degreePerPixel

                            masterTargetAngle = masterTargetAngle % 360
                            updateMasterAngle = True
                            masterSampleTime = time.time()
                            slaveTargetAngle = (masterTargetAngle + 180) % 360
                            updateSlaveAngle = True
                            logger.debug("Moving master to slave:", masterTargetAngle)

                speechDetected, micDOA = mic.speech_detected(), mic.direction
                speechMasterDiff = abs(micDOA - masterTargetAngle)
                if speechDetected and speechMasterDiff > SLAVE_MASTER_THRESHOLD and abs(micDOA - slaveTargetAngle) > ANGLE_THRESHOLD:
                    slaveTargetAngle = micDOA
                    logger.debug("Update slave angle:", slaveTargetAngle)
                    slaveSampleTime = time.time()
                    updateSlaveAngle = True


            # Send Serial Commands
            if updateSlaveAngle and updateMasterAngle:
                logger.debug("Slave Angle:", slaveTargetAngle)
                logger.debug("Master Angle:", masterTargetAngle)
                updateSlaveAngle = False
                updateMasterAngle = False
                if slaveCamID == BOT_CAM_ID:
                    mc.runMotors(masterTargetAngle, slaveTargetAngle)
                else:
                    mc.runMotors(slaveTargetAngle, masterTargetAngle)
            elif updateSlaveAngle:
                mc.runMotor(slaveCamID, slaveTargetAngle)
                logger.debug("Slave Angle:", slaveTargetAngle)
                updateSlaveAngle = False
            elif updateMasterAngle:
                mc.runMotor(masterCamID, masterTargetAngle)
                logger.debug("Master Angle:", masterTargetAngle)
                updateMasterAngle = False

            if DISPLAY_VIDEO:
                cv.imshow('Master Camera', masterFrame)
                cv.imshow('Slave Camera', slaveFrame)
                if cv.waitKey(1) == 27:
                    pass

        except KeyboardInterrupt:
            logger.debug("Keyboard interrupt! Terminating.")
            mc.stopMotors()
            slaveStream.stop()
            masterStream.stop()
            mic.close()
            time.sleep(2)
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
