# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

import time
import sys
import usb.core
import usb.util
import serial
from tuning import Tuning
from motor_control import MotorControl

TOP_CAM = "0"
BOT_CAM = "1"

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
    
    slaveCam = BOT_CAM;
    masterCam = TOP_CAM;

    while True:
        try:
            targetAngle = mic.direction
            ser.flushInput()
            ser.flushOutput()
            if slaveCam == BOT_CAM:
                mc.botMotor(targetAngle)
            else:
                mc.topMotor(targetAngle)

        except KeyboardInterrupt:
            print "Keyboard interrupt! Terminating."
            break

if __name__ == "__main__":
    main()
