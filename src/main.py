# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

import time
import math
import sys
import usb.core
import usb.util
import serial
from tuning import Tuning
from motor_control import MotorControl

stepSize = 1.8/8
stepsPerRev = 360/stepSize
motor1Id = 0
motor_cmd = "motor_set"
THRESHOLD = 20
CW = -1
CCW = 1

def main():
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) # Ubuntu VM
    time.sleep(3)
    
    mc = MotorControl()
    mc.runMotors(90, 270)
    sleep(2)
    mc.runMotors(MotorControl.CCW, 350, MotorControl.CW, 350)
    sleep(2)
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        sys.exit("Could not find ReSpeaker through USB")
#     ser.write("motor_set 1 1 350")
#     time.sleep(2)
#     ser.write("motor_set 0 0 350")
#     time.sleep(3)
#     ser.write("motor_set 1 0 350")
#     time.sleep(2)
#     ser.write("motor_set 0 1 350")
    prevAngle = 0;
    mic = Tuning(dev)
    mic.write("NONSTATNOISEONOFF", 1)
    mic.write("STATNOISEONOFF", 1)
    
    while True:
        try:
            # prev to ref
            # 0 to 65:
            # 65 to 0
            # 350 to 0
            # 0 to 270
            rotAngle = 0
            rotDir = CCW
            cwDiff = 0
            ccwDiff = 0

            refAngle = mic.direction
            print "refAngle:", refAngle, "prevAngle:", prevAngle
            diff = refAngle - prevAngle
            if abs(diff) < THRESHOLD:
                time.sleep(2)
                continue

            if refAngle < prevAngle:
                ccwDiff = (360 - prevAngle) + refAngle
                cwDiff = prevAngle - refAngle
            else:
                ccwDiff = refAngle - prevAngle
                cwDiff = prevAngle + (360 - refAngle)

            if cwDiff < ccwDiff:
                rotAngle = cwDiff
                rotDir = CW
                print "CW rotAngle:", rotAngle
            else:
                rotAngle = ccwDiff
                rotDir = CCW
                print "CCW rotAngle:", rotAngle
            if rotAngle > 180:
                print "~~~~~~~~~~~~ANGLE IS OVER 180 BAD MATH~~~~~~~~~~~~"
            cmd = buildMotorCommand(motor1Id, rotDir, rotAngle/stepSize)
            print cmd
            prevAngle = refAngle
            ser.flushInput()
            ser.flushOutput()
            ser.write(cmd)
            time.sleep(2) # minimum time for a 360 from a send command

        except KeyboardInterrupt:
            print "terminating"
            break

# dir 1 is CCW, else CW
# mic is CCW
def buildMotorCommand(motorId, rotDir, steps):
    return motor_cmd + " " + str(motorId) + " " + str(rotDir) + " " + str(int(steps))

if __name__ == "__main__":
    main()