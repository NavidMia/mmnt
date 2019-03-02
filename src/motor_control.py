import serial
import time

# bottom motor id: 1
# top motor id: 0
# motor_set ID DIR STEPS
# 1 revolution = 1600

# id 0 = top = right side of board
# id 1 = bottom = left side of board
# left/right corresponds to serial/dcin at the bottom for frame of reference

# serial command for setting motor:
#   motor_set <motor_id> <pos>
#   e.g.: motor_set 1 350

# serial command for setting multiple motor:
#   multi_motor_set <topPos> <botPos>
#   e.g.: multi_motor_set 90 270

# serial command for stopping motor:
#   motor_stop <motor_id>
#   e.g.: motor_stop 1

# serial command for stopping multiple motor:
#   multi_motor_stop
#   e.g.: multi_motor_stop

class MotorControl(object):
    MOTOR_SET_CMD = "motor_set"
    MULTI_MOTOR_SET_CMD = "multi_motor_set"
    MOTOR_STOP_CMD = "motor_stop"
    MULTI_MOTOR_STOP_CMD = "multi_motor_stop"
    TOP_MOTOR_ID = "0"
    BOT_MOTOR_ID = "1"
    CW = "1"
    CCW = "-1"
    
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        time.sleep(3)

    def build_serial_motor_cmd(self, motor_id, angle):
        return MOTOR_SET_CMD + " " + str(motor_id) + " " + str(angle)

    def build_serial_multi_motor_cmd(self, topAngle, botAngle):
        return MULTI_MOTOR_SET_CMD + " " + str(topAngle) + " " + str(botAngle)

    def build_serial_motor_stop_cmd(self, id):
        return MOTOR_STOP_CMD + " " + str(id)

    def build_serial_multi_motor_stop_cmd(self):
        return MULTI_MOTOR_STOP_CMD

    def topMotor(self, angle):
        cmd = self.build_serial_motor_cmd(TOP_MOTOR_ID, angle)
        self.ser.write(cmd)

    def botMotor(self, angle):
        cmd = self.build_serial_motor_cmd(BOT_MOTOR_ID, angle)
        self.ser.write(cmd)

    def runMotors(self, topAngle, botAngle):
        cmd = self.build_serial_multi_motor_cmd(topAngle, botAngle)
        self.ser.write(cmd)

    def stopTopMotor(self):
        cmd = self.build_serial_motor_stop_cmd(TOP_MOTOR_ID)
        self.ser.write(cmd)

    def stopTopMotor(self):
        cmd = self.build_serial_motor_stop_cmd(BOT_MOTOR_ID)
        self.ser.write(cmd)

    def stopMotors(self):
        cmd = self.build_serial_multi_motor_stop_cmd()
        self.ser.write(cmd)
