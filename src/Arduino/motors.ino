int dirPinTop = 3;
int stepperPinTop = 2;
int dirPinBot = 7;
int stepperPinBot = 6;
int msPinTop = 4;
int msPinBot = 5;

float stepSize = 1.8/8;
float stepsPerRev = 360/stepSize;
float gearRatio = 36/45;

float topPos = 0;
float topTargetPos = 0;
int topDir = 1; // -1 = CCW, 1 = CW
bool stepTop = false;

float botPos = 0;
float botTargetPos = 0;
int botDir = 1; // -1 = CCW, 1 = CW
bool stepBot = false;

#define POS_THRESHOLD (0.8)
#define TOP_PULSE_DELAY (1) // delay in milliseconds
#define BOT_PULSE_DELAY (2) // delay in milliseconds
#define DIR_WRITE_DELAY (50) // delay in milliseconds
#define CW (1)
#define CCW (-1)
#define TOP_MOTOR_ID (0)
#define BOT_MOTOR_ID (1)

// 300 microseconds is the lowest delay possible with power supply
// 1000 microseconds otherwise
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
                topTargetPos = atoi(strtok(NULL, " "));
            } else if (id == BOT_MOTOR_ID) {
                botTargetPos = atoi(strtok(NULL, " "));
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
            topTargetPos = atoi(strtok(NULL, " "));
        } else if (i == 1) {
            botTargetPos = atoi(strtok(NULL, " "));
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
    if (topPos - topTargetPos < POS_THRESHOLD) {
        float ccwDiff = (360 - topPos + topTargetPos) % 360;
        float cwDiff = 360 - ccwDiff;
        int newTopDir = cwDiff < ccwDiff ? CW : CCW;
        
        if (newTopDir != topDir) {
            topDir = newTopDir;
            digitalWrite(dirPinTop, topDir == CW ? true : false);
            delay(DIR_WRITE_DELAY);
        }
        stepTop = true;
    } else {
        stepTop = false;
    }

    // Check if bot motor needs to be rotated
    if (botPos - botTargetPos < POS_THRESHOLD) {
        float ccwDiff = (360 - botPos + botTargetPos) % 360;
        float cwDiff = 360 - ccwDiff;
        int newBotDir = cwDiff < ccwDiff ? CW : CCW;
        
        if (newBotDir != botDir) {
            botDir = newBotDir;
            digitalWrite(dirPinBot, botDir == CW ? true : false);
            delay(DIR_WRITE_DELAY);
        }
        stepBot = true;
    } else {
        stepBot = false;
    }

    // rotate motors if needed
    if (stepTop && stepBot) {
        digitalWrite(stepperPinTop, HIGH);
        digitalWrite(stepperPinBot, HIGH);
        delay(TOP_PULSE_DELAY);
        digitalWrite(stepperPinTop, LOW);
        delay(BOT_PULSE_DELAY - TOP_PULSE_DELAY);
        digitalWrite(stepperPinBot, LOW);
        topPos = abs((topPos + topDir * stepSize) % 360);
        botPos = abs((botPos + botDir * stepSize) % 360);
    } else if (stepTop) {
        digitalWrite(stepperPinTop, HIGH);
        delay(TOP_PULSE_DELAY);
        digitalWrite(stepperPinTop, LOW);
        topPos = abs((topPos + topDir * stepSize) % 360);
    } else if (stepBot) {
        digitalWrite(stepperPinBot, HIGH);
        delay(BOT_PULSE_DELAY);
        digitalWrite(stepperPinBot, LOW);
        botPos = abs((botPos + botDir * stepSize) % 360);
    }
}
