int dirPinBot = 3;
int stepperPinBot = 2;
int msPinBot = 4;
int dirPinTop = 7;
int stepperPinTop = 6;
int msPinTop = 5;

float stepSize = 1.8/8;
float stepsPerRev = 360/stepSize;
float gearRatio = 36.0/45.0;

float topPos = 0;
float topTargetPos = 0;
int topDir = 1; // 1 = CCW, -1 = CW
bool stepTop = false;

float botPos = 0;
float botTargetPos = 0;
int botDir = 1; // 1 = CCW, -1 = CW
bool stepBot = false;

#define POS_THRESHOLD (2)
#define TOP_PULSE_DELAY (1500) // delay in microseconds
#define BOT_PULSE_DELAY (1500) // delay in microseconds
#define DIR_WRITE_DELAY (50) // delay in milliseconds
#define CW (-1)
#define CCW (1)
#define BOT_MOTOR_ID (0)
#define TOP_MOTOR_ID (1)
#define STEPS (10)

void setup() {
    pinMode(dirPinTop, OUTPUT);
    pinMode(stepperPinTop, OUTPUT);
    pinMode(dirPinBot, OUTPUT);
    pinMode(stepperPinBot, OUTPUT);
    pinMode(msPinTop, OUTPUT);
    pinMode(msPinBot, OUTPUT);

    digitalWrite(msPinTop, HIGH);
    digitalWrite(msPinBot, HIGH);

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
    Serial.print("stopping motors\n");
    topTargetPos = topPos;
    botTargetPos = botPos;
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

    // rotate motors if needed
    if (stepTop && stepBot) {
        if (topDir != botDir) {
            for (int i = 0; i < STEPS; i++) {
                if (i < STEPS/2) digitalWrite(stepperPinBot, HIGH);
                digitalWrite(stepperPinTop, HIGH);
                delayMicroseconds(BOT_PULSE_DELAY);
                if (i < STEPS/2) digitalWrite(stepperPinBot, LOW);
                digitalWrite(stepperPinTop, LOW);
            }
            topPos = topPos + topDir * stepSize * STEPS/2 * gearRatio;
            botPos = botPos + botDir * stepSize * STEPS/2 * gearRatio;
        } else {
            for (int i = 0; i < STEPS; i++) {
                digitalWrite(stepperPinBot, HIGH);
                delayMicroseconds(BOT_PULSE_DELAY);
                digitalWrite(stepperPinBot, LOW);
            }
            topPos = topPos + topDir * stepSize * STEPS * gearRatio;
            botPos = botPos + botDir * stepSize * STEPS * gearRatio;
        }
        if (topPos < 0) {
            topPos = 360 - topPos;
        } else if (topPos > 359) {
            topPos = topPos - 359;
        }
        if (botPos < 0) {
            botPos = 360 - botPos;
        } else if (botPos > 359) {
            botPos = botPos - 359;
        }
    } else if (stepTop) {
        for (int i = 0; i < STEPS; i++) {
            digitalWrite(stepperPinTop, HIGH);
            delayMicroseconds(TOP_PULSE_DELAY);
            digitalWrite(stepperPinTop, LOW);
        }
        topPos = topPos + topDir * stepSize * STEPS * gearRatio;
        if (topPos < 0) {
            topPos = 360 - topPos;
        } else if (topPos > 359) {
            topPos = topPos - 359;
        }
    } else if (stepBot) {
        if (topDir == botDir) {
            topDir = botDir * -1;
            digitalWrite(dirPinTop, topDir == CW ? true : false);
        }
        for (int i = 0; i < STEPS; i++) {
            digitalWrite(stepperPinBot, HIGH);
            digitalWrite(stepperPinTop, HIGH);
            delayMicroseconds(BOT_PULSE_DELAY);
            digitalWrite(stepperPinBot, LOW);
            digitalWrite(stepperPinTop, LOW);
        }
        botPos = botPos + botDir * stepSize * STEPS * gearRatio;
        if (botPos < 0) {
            botPos = 360 - botPos;
        } else if (botPos > 359) {
            botPos = botPos - 359;
        }
    }
}
