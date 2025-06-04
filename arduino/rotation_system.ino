#include <Servo.h>
#include <Wire.h>
#include "Adafruit_VL53L1X.h"

// --------- Servo Instellingen ---------
Servo servos[10];  // ID 0 wordt niet gebruikt

int servoPins[10] = {
  -1, 3, 5, 6, 7, 8, 9, 10, 11, 12
};

int STOP_PWM[10] = {
  0, 365, 365, 90, 90, 368, 368, 200, 90, 90
};

// --------- Sensoren ---------
#define ENDSTOP_1 8  // D8
#define ENDSTOP_2 9  // D9
#define BEAM_1 4     // D4
#define BEAM_2 5     // D5

// --------- Hoogte Sensor ---------
Adafruit_VL53L1X vl = Adafruit_VL53L1X();
unsigned long lastHeightTime = 0;
int heightInterval = 250;  // in ms

// --------- millis() Rotatievariabelen ---------
unsigned long rotateStartTime = 0;
unsigned long rotateDuration = 0;
int rotateServoId = 0;
bool rotating = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Servo's initialiseren
  for (int i = 1; i <= 9; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].writeMicroseconds(STOP_PWM[i]);
  }

  // Sensoren instellen
  pinMode(ENDSTOP_1, INPUT_PULLUP);
  pinMode(ENDSTOP_2, INPUT_PULLUP);
  pinMode(BEAM_1, INPUT);
  pinMode(BEAM_2, INPUT);

  // VL53L1X initialiseren
  if (!vl.begin()) {
    Serial.println("VL53L1X niet gevonden");
    while (1);
  }
  vl.setDistanceMode(VL53L1X::LONG);
  vl.setTimingBudget(50);
  vl.startRanging();
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    handleCommand(input);
  }

  updateRotation(); // millis()-gebaseerde draai-update

  // Hoogte uitlezen
  unsigned long now = millis();
  if (now - lastHeightTime >= heightInterval) {
    if (vl.dataReady()) {
      int dist = vl.read();
      Serial.print("HEIGHT:");
      Serial.println(dist);
      vl.clearInterrupt();
    }
    lastHeightTime = now;
  }
}

// --------- Commando Handler ---------

void handleCommand(String cmd) {
  Serial.print("CMD: ");
  Serial.println(cmd);

  if (cmd.startsWith("SET")) {
    int id, pwm;
    char dirBuf[4];
    sscanf(cmd.c_str(), "SET %d %s %d", &id, dirBuf, &pwm);
    String dir = String(dirBuf);
    handleSet(id, dir, pwm);
  } else if (cmd.startsWith("ROTATE")) {
    int id, angle;
    sscanf(cmd.c_str(), "ROTATE %d %d", &id, &angle);
    handleRotate(id, angle);
  } else if (cmd == "GET ENDSTOPS") {
    Serial.print("e1");
    Serial.print(digitalRead(ENDSTOP_1) == LOW ? "1 " : "0 ");
    Serial.print("e2");
    Serial.println(digitalRead(ENDSTOP_2) == LOW ? "1" : "0");
  } else if (cmd == "GET BEAMS") {
    Serial.print(digitalRead(BEAM_1) == LOW ? "b11 " : "b10 ");
    Serial.println(digitalRead(BEAM_2) == LOW ? "b21" : "b20");
  }
}

// --------- Actie Functies ---------

void handleSet(int id, String dir, int pwm) {
  if (id < 1 || id > 9) return;

  if (dir == "FWD") {
    servos[id].writeMicroseconds(pwm);
  } else if (dir == "REV") {
    servos[id].writeMicroseconds(600 - pwm);  // omkeren
  } else if (dir == "STOP") {
    servos[id].writeMicroseconds(STOP_PWM[id]);
  }
}

void handleRotate(int id, int angle) {
  if (id < 1 || id > 9) return;

  int pwm = 200;
  servos[id].writeMicroseconds(pwm);
  rotateServoId = id;
  rotateStartTime = millis();
  rotateDuration = map(angle, 0, 180, 0, 2000);  // afgesteld op kalibratie
  rotating = true;
}

void updateRotation() {
  if (rotating && millis() - rotateStartTime >= rotateDuration) {
    servos[rotateServoId].writeMicroseconds(STOP_PWM[rotateServoId]);
    rotating = false;
  }
}
