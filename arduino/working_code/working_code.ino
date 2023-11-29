#include <Servo.h>

Servo FL, FR, RL, RR, BL, BR;

const int FL_PIN = 3;
const int FR_PIN = 5;
const int RL_PIN = 6;
const int RR_PIN = 9;
const int BL_PIN = 10;
const int BR_PIN = 11;

const int LIGHT1_PIN = 12;
const int LIGHT2_PIN = 13;


void setup() {
  FL.attach(FL_PIN);
  FR.attach(FR_PIN);
  RL.attach(RL_PIN);
  RR.attach(RR_PIN);
  BL.attach(BL_PIN);
  BR.attach(BR_PIN);

  pinMode(LIGHT1_PIN, OUTPUT);
  pinMode(LIGHT2_PIN, OUTPUT);
  stopMotors();
  turnOffLights();
  delay(2000);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming data
    String data = Serial.readStringUntil('\n');

    // Process the received data
    String strings[6];
    int index = 0;
    char *ptr = strtok((char *)data.c_str(), ",");
    while (ptr != NULL && index < 6) {
      strings[index] = ptr;
      ptr = strtok(NULL, ",");
      index++;
    }

    float x = atof(strings[1].c_str());

    if ((-0.01 > x) || (x > 0.01)) {
      int xsignal = mapFloat(x, -1.00, 1.00, 2000, 1000);
      motor4_value(xsignal);
    } else {
      motors4_middle();
    }


    float y = atof(strings[3].c_str());

    if (y > 0.01) {
      int ysignal = mapFloat(y, 0.00, 1.00, 1000, 2000);
      motor2_value(ysignal);
    } else {
      motors2_off();
    }


if (strings[4] == "True") {
      // Toggle the LED
      digitalWrite(LIGHT1_PIN, !digitalRead(LIGHT1_PIN));
      delay(500); // Add a delay for visibility (optional)
    }
    if (strings[5] == "True") {
      // Toggle the LED
      digitalWrite(LIGHT2_PIN, !digitalRead(LIGHT2_PIN));
      delay(500); // Add a delay for visibility (optional)
    }

 

  }
}

int mapFloat(float x, float in_min, float in_max, int out_min, int out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void motors4_middle() {
  FL.writeMicroseconds(1500);
  FR.writeMicroseconds(1500);
  RL.writeMicroseconds(1500);
  RR.writeMicroseconds(1500);
}

void motors2_off() {
  BL.writeMicroseconds(1000);
  BR.writeMicroseconds(1000);
}

void motor4_value(int x) {
  FL.writeMicroseconds(x);
  FR.writeMicroseconds(x);
  RL.writeMicroseconds(x);
  RR.writeMicroseconds(x);
}
void motor2_value(int x) {
  BL.writeMicroseconds(x);
  BR.writeMicroseconds(x);
}

void stopMotors() {
  FL.writeMicroseconds(1500);
  FR.writeMicroseconds(1500);
  RL.writeMicroseconds(1500);
  RR.writeMicroseconds(1500);
  BL.writeMicroseconds(1000);
  BR.writeMicroseconds(1000);
}

void turnOffLights() {
  digitalWrite(LIGHT1_PIN, LOW);
  digitalWrite(LIGHT2_PIN, LOW);
}
