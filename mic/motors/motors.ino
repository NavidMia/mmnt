int dirPinTop = 3;
int stepperPinTop = 2;
int dirPinBot = 7;
int stepperPinBot = 6;
int msPinTop = 4;
int msPinBot = 5;

float stepSize = 1.8/8;
int stepsPerRev = 360/stepSize;
int topMotorPos = 0;
int botMotorPos = 0;

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

void step_motors(int dirTop, int stepsTop, int dirBot, int stepsBot) {
  digitalWrite(dirPinTop, bool(dirTop));
  digitalWrite(dirPinBot, bool(dirBot));

  delay(50);
  for(int i = 0; i < steps; i++) {
    digitalWrite(stepperPinTop, HIGH);
    digitalWrite(stepperPinBot, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepperPinTop, LOW);
    // Bot motor needs more delay for more torque
    delayMicroseconds(1000);
    digitalWrite(stepperPinBot, LOW);
    delayMicroseconds(1000);
  }
}

void step_individual(int id, int dir, int steps) {
  int dirPin, stepperPin;
  if (id == 0) {
    dirPin = dirPinTop;
    stepperPin = stepperPinTop;
  } else {
    dirPin = dirPinBot;
    stepperPin = stepperPinBot;
  }

  if (dir == 1) {
    digitalWrite(dirPin, true);
  } else {
    digitalWrite(dirPin, false);
  }
  
  delay(50);
  for(int i=0;i<steps;i++){
    digitalWrite(stepperPin, HIGH);
    if (id == 0) {
      delayMicroseconds(1000);
    } else {
      delayMicroseconds(2000);
    }
    digitalWrite(stepperPin, LOW);
    if (id == 0) {
      delayMicroseconds(1000);
    } else {
      delayMicroseconds(2000);
    }
  }
}

// serial command for setting motor:
//   motor_set <motor_id> <direction> <steps>
//   e.g.: motor_set 1 1 350
void handleMotorSetCommand() {
  int id = 0;
  int dir = 1;
  int steps = 1;
  for (int i = 0; i < 3; i++) {
    if (i == 0) {
      id = atoi(strtok(NULL, " "));
    } else if (i == 1) {
      dir = atoi(strtok(NULL, " "));
    } else if (i == 2) {
      steps = atoi(strtok(NULL, " "));
    }
  }
  step_individual(id, dir, steps);
}

// serial command for setting multiple motor:
//   multi_motor_set <dir1> <steps1> <dir2> <steps2>
//   e.g.: multi_motor_set 1 350 1 350
void handleMultiMotorSetCommand() {
  int dirTop = 0;
  int dirBot = 0;
  int stepsTop = 1;
  int stepsBot = 1;
  for (int i = 0; i < 4; i++) {
    if (i == 0) {
      dirTop = atoi(strtok(NULL, " "));
    } else if (i == 1) {
      stepsTop = atoi(strtok(NULL, " "));
    } else if (i == 2) {
      dirBot = atoi(strtok(NULL, " "));
    } else if (i == 3) {
      stepsBot = atoi(strtok(NULL, " "));
    }
  }
  step_motors(dirTop, stepsTop, dirBot, stepsBot)
}

void handleMotorStopCommand() {
  digitalWrite(stepperPinTop, LOW);
  digitalWrite(stepperPinBot, LOW);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    char *str = command.c_str();
    char *arg = strtok(str, " ");
    while (arg != NULL) {
      if (!strcmp(arg, "motor_set")) {
        handleMotorSetCommand();
      } else if (!strcmp(arg, "multi_motor_set")) {
        handleMultiMotorSetCommand();
      } else if (!strcmp(arg, "motor_stop")) {
        handleMotorStopCommand();
      }
      arg = strtok(NULL, " ");
    }
  }
}
