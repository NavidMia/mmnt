import serial
import time

def main():
	# ser = serial.Serial("/dev/tty.usbmodem14201", 9600, timeout=1)
	# ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) # Ubuntu VM
	ser = serial.Serial("/dev/tty.usbmodem14301", 9600, timeout=1) # OSX
	time.sleep(3)
	print("sending cmd")
	ser.write("motor_set 0 -1 1600")

if __name__ == "__main__":
    main()