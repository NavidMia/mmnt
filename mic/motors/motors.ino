int dirPin1 = 3;
int stepperPin1 = 2;
int dirPin2 = 7;
int stepperPin2 = 6;
int ms1Pin = 4;
int ms2Pin = 5;

float stepSize = 1.8/8;
int stepsPerRev = 360/stepSize;


// 300 microseconds is the lowest delay possible with power supply
// 1000 microseconds otherwise
void setup() {
  pinMode(dirPin1, OUTPUT);
  pinMode(stepperPin1, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(stepperPin2, OUTPUT);
  pinMode(ms1Pin, OUTPUT);
  pinMode(ms2Pin, OUTPUT);

  digitalWrite(ms1Pin, HIGH);
  digitalWrite(ms2Pin, HIGH);

  Serial.begin(9600);
}

void step(boolean dir,int steps){
  if (dir == 1) {
    digitalWrite(dirPin1, true);
    digitalWrite(dirPin2, true); 
  } else {
    digitalWrite(dirPin1, false);
    digitalWrite(dirPin2, false); 
  }
  delay(50);
  for(int i=0;i<steps;i++){
    digitalWrite(stepperPin1, HIGH);
    digitalWrite(stepperPin2, HIGH);
    delayMicroseconds(300);
    digitalWrite(stepperPin1, LOW);
    digitalWrite(stepperPin2, LOW);
    delayMicroseconds(300);
  }
}

void step_individual(int id, int dir, int steps) {
  int dirPin, stepperPin;
  if (id == 0) {
    dirPin = dirPin1;
    stepperPin = stepperPin1;
  } else {
    dirPin = dirPin2;
    stepperPin = stepperPin2;
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
//  step(dir, steps);
}

void loop(){
  if (Serial.available()) {
    String command = Serial.readString();
    char *str = command.c_str();
    char *arg = strtok(str, " ");
    while (arg != NULL) {
      if (!strcmp(arg, "motor_set")) {
        handleMotorSetCommand(); 
      }
      arg = strtok(NULL, " ");
    }
  }
}
