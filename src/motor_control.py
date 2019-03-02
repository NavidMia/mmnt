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
#   motor_set <motor_id> <direction> <steps>   
#   e.g. motor_set 1 1 350

# serial command for setting multiple motor:
#   multi_motor_set <dirTop> <stepsTop> <dirBot> <stepsBot>
#   e.g.: multi_motor_set 1 350 1 350

class MotorControl(object):
    MOTOR_SET_CMD = "motor_set"
    MULTI_MOTOR_SET_CMD = "multi_motor_set"
    MOTOR_STOP_CMD = "motor_stop"
    TOP_MOTOR_ID = "0"
    BOT_MOTOR_ID = "1"
    CW = "0"
    CCW = "1"
    
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        time.sleep(3)

    def build_serial_motor_cmd(self, motor_id, direction, steps):
        return MOTOR_SET_CMD + " " + str(motor_id) + " " + str(direction) + " " + str(steps)

    def build_serial_multi_motor_cmd(self, dirTop, stepsTop, dirBot, stepsBot):
        return MULTI_MOTOR_SET_CMD + " " + str(dirTop) + " " + str(stepsTop) + " " + str(dirBot) + " " + str(stepsBot)

    def build_serial_motor_stop_cmd(self):
        return MOTOR_STOP_CMD

    def topMotor(self, direction, steps):
        cmd = self.build_serial_motor_cmd(TOP_MOTOR_ID, direction, steps)
        self.ser.write(cmd)

    def botMotor(self, direction, steps):
        cmd = self.build_serial_motor_cmd(BOT_MOTOR_ID, direction, steps)
        self.ser.write(cmd)

    def runMotors(self, dirTop, stepsTop, dirBot, stepsBot):
        cmd = self.build_serial_multi_motor_cmd(dirTop, stepsTop, dirBot, stepsBot)
        self.ser.write(cmd)

    # def stopMotors(self):
    #     cmd = self.build_serial_motor_stop_cmd()
    #     self.ser.write(cmd)
