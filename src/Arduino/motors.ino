int dirPinTop = 3;
int stepperPinTop = 2;
int msPinTop = 4;
int dirPinBot = 7;
int stepperPinBot = 6;
int msPinBot = 5;
int sleepPin = 13;

float stepSize = 1.8/8;
float gearRatio = 36.0/45.0;

bool sleep = true;
unsigned long sleepStart = millis();

#define POS_THRESHOLD (2)

#define MAX_PULSE_DELAY (5000)
#define MIN_PULSE_DELAY (1500)
#define UPPER_DELAY_ANGLE (20)
#define LOWER_DELAY_ANGLE (0)
#define DELAY_GAIN ((MAX_PULSE_DELAY - MIN_PULSE_DELAY)/(LOWER_DELAY_ANGLE - UPPER_DELAY_ANGLE))

#define DIR_WRITE_DELAY (50) // delay in milliseconds
#define CW (-1)
#define CCW (1)
#define BOT_MOTOR_ID (0)
#define TOP_MOTOR_ID (1)
#define STEPS (10)

#define BOT_MOTOR_INITIAL_POS (180)
#define TOP_MOTOR_INITIAL_POS (0)

float topPos = TOP_MOTOR_INITIAL_POS;
float topTargetPos = TOP_MOTOR_INITIAL_POS;
int topDir = 1; // 1 = CCW, -1 = CW
bool stepTop = false;

float botPos = BOT_MOTOR_INITIAL_POS;
float botTargetPos = BOT_MOTOR_INITIAL_POS;
int botDir = 1; // 1 = CCW, -1 = CW
bool stepBot = false;
void setup() {
    pinMode(dirPinTop, OUTPUT);
    pinMode(stepperPinTop, OUTPUT);
    pinMode(dirPinBot, OUTPUT);
    pinMode(stepperPinBot, OUTPUT);
    pinMode(msPinTop, OUTPUT);
    pinMode(msPinBot, OUTPUT);
    pinMode(sleepPin, OUTPUT);

    digitalWrite(msPinTop, HIGH);
    digitalWrite(msPinBot, HIGH);
    digitalWrite(sleepPin, LOW);

    Serial.begin(9600);
}

// serial command for setting motor:
//   motor_set <motor_id> <pos>
//   e.g.: motor_set 1 350
void handleMotorSetCommand() {
    int id = 0;
    for (int i = 0; i < 2; i++) {
        if (i == 0) {
            id = atoi(strtok(NULL, " "));
        } else if (i == 1) {
            if (id == TOP_MOTOR_ID) {
                topTargetPos = atoi(strtok(NULL, " ")) % 360;
            } else if (id == BOT_MOTOR_ID) {
                botTargetPos = atoi(strtok(NULL, " ")) % 360;
            }
        }
    }
}

// serial command for setting multiple motor:
//   multi_motor_set <topPos> <botPos>
//   e.g.: multi_motor_set 90 270
void handleMultiMotorSetCommand() {
    for (int i = 0; i < 2; i++) {
        if (i == 0) {
            topTargetPos = atoi(strtok(NULL, " ")) % 360;
        } else if (i == 1) {
            botTargetPos = atoi(strtok(NULL, " ")) % 360;
        }
    }
}

// serial command for stopping motor:
//   motor_stop <motor_id>
//   e.g.: motor_stop 1
void handleMotorStopCommand() {
    int id = atoi(strtok(NULL, " "));
    if (id == TOP_MOTOR_ID) {
        topTargetPos = topPos;
    } else if (id == BOT_MOTOR_ID) {
        botTargetPos = botPos;
    }
}

// serial command for stopping multiple motor:
//   multi_motor_stop
//   e.g.: multi_motor_stop
void handleMultiMotorStopCommand() {
    topTargetPos = topPos;
    botTargetPos = botPos;
}

// serial command for resetting motor positions:
//   reset_motors
//   e.g.: reset_motors
void handleResetMotorsCommand() {
    topTargetPos = TOP_MOTOR_INITIAL_POS;
    botTargetPos = BOT_MOTOR_INITIAL_POS;
}

void loop() {
    // Check if new command is available and parse it to update motor parameters
    if (Serial.available()) {
        String command = Serial.readString();
        char *str = command.c_str();
        char *cmd = strtok(str, " ");
        while (cmd != NULL) {
            if (!strcmp(cmd, "motor_set")) {
                handleMotorSetCommand();
            } else if (!strcmp(cmd, "multi_motor_set")) {
                handleMultiMotorSetCommand();
            } else if (!strcmp(cmd, "motor_stop")) {
                handleMotorStopCommand();
            } else if (!strcmp(cmd, "multi_motor_stop")) {
                handleMultiMotorStopCommand();
            } else if (!strcmp(cmd, "reset_motors")) {
                handleResetMotorsCommand();
            }
            cmd = strtok(NULL, " ");
        }
    }

    // Check if top motor needs to be rotated
    if (abs(topPos - topTargetPos) > POS_THRESHOLD) {
        int ccwDiff = int(360 - topPos + topTargetPos) % 360;
        int cwDiff = 360 - ccwDiff;
        int newTopDir = cwDiff < ccwDiff ? CW : CCW;
        
        if (newTopDir != topDir) {
            topDir = newTopDir;
            digitalWrite(dirPinTop, topDir == CW ? true : false);
        }
        stepTop = true;
    } else {
        stepTop = false;
    }

    // Check if bot motor needs to be rotated
    if (abs(botPos - botTargetPos) > POS_THRESHOLD) {
        int ccwDiff = int(360 - botPos + botTargetPos) % 360;
        int cwDiff = 360 - ccwDiff;
        int newBotDir = cwDiff < ccwDiff ? CW : CCW;
        
        if (newBotDir != botDir) {
            botDir = newBotDir;
            digitalWrite(dirPinBot, botDir == CW ? true : false);
        }
        stepBot = true;
    } else {
        stepBot = false;
    }

    if ((stepTop || stepBot) && sleep) {
        digitalWrite(sleepPin, HIGH);
        sleep = false;
        sleepStart = millis();
    } else if (!(stepTop || stepBot) && !sleep && ((millis() - sleepStart) > 2000)) {
        digitalWrite(sleepPin, LOW);
        sleep = true;
    }

    // rotate motors if needed
    if (stepTop && stepBot) {
        int targetDiff = abs(int(botPos - botTargetPos));
        int stepDelay = DELAY_GAIN * min(targetDiff, UPPER_DELAY_ANGLE) + MAX_PULSE_DELAY;
        if (topDir != botDir) {
            for (int i = 0; i < STEPS; i++) {
                if (i < STEPS/2) digitalWrite(stepperPinBot, HIGH);
                digitalWrite(stepperPinTop, HIGH);
                delayMicroseconds(stepDelay);
                if (i < STEPS/2) digitalWrite(stepperPinBot, LOW);
                digitalWrite(stepperPinTop, LOW);
            }
            topPos = topPos + topDir * stepSize * STEPS/2 * gearRatio;
            botPos = botPos + botDir * stepSize * STEPS/2 * gearRatio;
        } else {
            for (int i = 0; i < STEPS; i++) {
                digitalWrite(stepperPinBot, HIGH);
                delayMicroseconds(stepDelay);
                digitalWrite(stepperPinBot, LOW);
            }
            topPos = topPos + topDir * stepSize * STEPS * gearRatio;
            botPos = botPos + botDir * stepSize * STEPS * gearRatio;
        }
        if (topPos < 0) {
            topPos = 360 + topPos;
        } else if (topPos > 359) {
            topPos = topPos - 359;
        }
        if (botPos < 0) {
            botPos = 360 + botPos;
        } else if (botPos > 359) {
            botPos = botPos - 359;
        }
    } else if (stepTop) {
        int targetDiff = abs(int(topPos - topTargetPos));
        int stepDelay = DELAY_GAIN * min(targetDiff, UPPER_DELAY_ANGLE) + MAX_PULSE_DELAY;
        for (int i = 0; i < STEPS; i++) {
            digitalWrite(stepperPinTop, HIGH);
            delayMicroseconds(stepDelay);
            digitalWrite(stepperPinTop, LOW);
        }
        topPos = topPos + topDir * stepSize * STEPS * gearRatio;
        if (topPos < 0) {
            topPos = 360 + topPos;
        } else if (topPos > 359) {
            topPos = topPos - 359;
        }
    } else if (stepBot) {
        int targetDiff = abs(int(botPos - botTargetPos));
        int stepDelay = DELAY_GAIN * min(targetDiff, UPPER_DELAY_ANGLE) + MAX_PULSE_DELAY;

        if (topDir == botDir) {
            topDir = botDir * -1;
            digitalWrite(dirPinTop, topDir == CW ? true : false);
        }
        for (int i = 0; i < STEPS; i++) {
            digitalWrite(stepperPinBot, HIGH);
            digitalWrite(stepperPinTop, HIGH);
            delayMicroseconds(stepDelay);
            digitalWrite(stepperPinBot, LOW);
            digitalWrite(stepperPinTop, LOW);
        }
        botPos = botPos + botDir * stepSize * STEPS * gearRatio;
        if (botPos < 0) {
            botPos = 360 + botPos;
        } else if (botPos > 359) {
            botPos = botPos - 359;
        }
    }
}
