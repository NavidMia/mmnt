import serial
import time

# bottom motor id: 1
# top motor id: 0
# motor_set ID DIR STEPS
# 1 revolution = 1600

# id 0 = top = right side of board
# id 1 = bottom = left side of board
# left/right corresponds to serial/dcin at the bottom for frame of reference

def main():
    # ser = serial.Serial("/dev/tty.usbmodem14201", 9600, timeout=1)
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    time.sleep(3)
    print("sending cmd")
    # ser.write("motor_set 0 1 1600")
    ser.write("motor_set 1 1 350")
    time.sleep(2)
    ser.write("motor_set 0 0 350")
    time.sleep(3)
    ser.write("motor_set 1 0 350")
    time.sleep(2)
    ser.write("motor_set 0 1 350")

if __name__ == "__main__":
    main()