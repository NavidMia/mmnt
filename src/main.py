import usb.core
import usb.util
import serial
import time
from motor_control import MotorControl

def main():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) # Ubuntu VM
    time.sleep(3)

    mc = MotorControl()
    mc.runMotors(MotorControl.CW, 350, MotorControl.CCW, 350)

if __name__ == "__main__":
    main()
