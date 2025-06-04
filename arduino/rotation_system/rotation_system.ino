// rotation_system.ino
#include <Wire.h>
#include <Adafruit_VL53L1X.h>
#include <Adafruit_PWMServoDriver.h>
#include <Servo.h>

// Servo controller (PCA9685)
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Hoogtesensor
Adafruit_VL53L1X vl53 = Adafruit_VL53L1X();

// Servo-waarden
#define SERVO_MIN 100  // minimum pulse length
#define SERVO_MAX 600  // maximum pulse length

// Pins voor endstops en beam sensors
#define ENDSTOP1_PIN 8
#define ENDSTOP2_PIN 9
#define BEAM1_PIN 4
#define BEAM2_PIN 5

// Tracking van bewegingen
unsigned long pushStart = 0;
bool pushing = false;
int pushChannel = -1;
int pushDuration = 0;
int pushPWM = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Start PWM driver
  pwm.begin();
  pwm.setPWMFreq(60);

  // Start VL53L1X
  if (!vl53.begin()) {
    Serial.println("VL53L1X niet gevonden!");
    while (1);
  }
  vl53.setDistanceMode(VL53L1X::LONG);
  vl53.setTimingBudget(50);
  vl53.startRanging();

  // Setup sensors
  pinMode(ENDSTOP1_PIN, INPUT_PULLUP);
  pinMode(ENDSTOP2_PIN, INPUT_PULLUP);
  pinMode(BEAM1_PIN, INPUT_PULLUP);
  pinMode(BEAM2_PIN, INPUT_PULLUP);

  Serial.println("[ARDUINO] Systeem klaar");
}

void loop() {
  // Check serial input
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }

  // Non-blocking push
  if (pushing && millis() - pushStart >= pushDuration) {
    pwm.setPWM(pushChannel, 0, SERVO_MIN + 365); // STOP
    pushing = false;
  }
}

void handleCommand(String cmd) {
  Serial.print("CMD: "); Serial.println(cmd);

  if (cmd.startsWith("SET")) {
    int s = cmd.substring(4, 5).toInt();
    String dir = cmd.substring(6, 9);
    int pwm = cmd.substring(10).toInt();
    if (dir == "FWD") pwm.setPWM(s, 0, SERVO_MIN + pwm);
    else if (dir == "REV") pwm.setPWM(s, 0, SERVO_MIN + (4096 - pwm));
    else pwm.setPWM(s, 0, SERVO_MIN + 365); // stop
  }

  else if (cmd.startsWith("ROTATE")) {
    int ch = cmd.substring(7, 8).toInt();
    int angle = cmd.substring(9).toInt();
    int pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
    pwm.setPWM(ch, 0, pulse);
  }

  else if (cmd.startsWith("PUSH")) {
    pushChannel = cmd.substring(5, 6).toInt();
    pushPWM = cmd.substring(7, 10).toInt();
    pushDuration = cmd.substring(11).toInt();
    pushStart = millis();
    pushing = true;
    pwm.setPWM(pushChannel, 0, SERVO_MIN + pushPWM);
  }

  else if (cmd == "GET ENDSTOPS") {
    String status = "e10 ";
    status += digitalRead(ENDSTOP1_PIN) == LOW ? "1" : "0";
    status += " e11 ";
    status += digitalRead(ENDSTOP2_PIN) == LOW ? "1" : "0";
    Serial.println(status);
  }

  else if (cmd == "GET BEAMS") {
    String b = "b10 ";
    b += digitalRead(BEAM1_PIN) == LOW ? "1" : "0";
    b += " b11 ";
    b += digitalRead(BEAM2_PIN) == LOW ? "1" : "0";
    Serial.println(b);
  }

  else if (cmd == "GET HEIGHT") {
    VL53L1X_Result_t result;
    if (vl53.read(true, &result)) {
      Serial.print("HEIGHT: ");
      Serial.println(result.distance);
    } else {
      Serial.println("HEIGHT: ERROR");
    }
  }

  else {
    Serial.println("[ERROR] Onbekend commando");
  }
}
