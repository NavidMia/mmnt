# sudo chmod 666 /dev/ttyACM0
# lsusb - find which usb device corresponds to the mic
# sudo chmod o+rw /dev/bus/usb/001/003

from tuning import Tuning
import usb.core
import usb.util
import serial
import time
import math

stepSize = 1.8/8
stepsPerRev = 360/stepSize
motor1Id = 0
motor_cmd = "motor_set"
THRESHOLD = 20
CW = -1
CCW = 1

def main():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    # ser = serial.Serial("/dev/tty.usbmodem14201", 9600, timeout=1)
    # ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) # Ubuntu VM
    ser = serial.Serial("/dev/tty.usbmodem14301", 9600, timeout=1) # OSX
    time.sleep(3)
    
    prevAngle = 0;

    if dev:
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