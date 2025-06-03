#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO_STOP_DEFAULT 365
#define SERVO_STOP_SERVO7 368
#define SERVO_PWM_MOVE 200
#define POS_MIN 90
#define POS_MAX 530

#define PUSHER1_ENDSTOP_PIN 8
#define PUSHER2_ENDSTOP_PIN 9

int custom_pwm[9] = {
  SERVO_STOP_DEFAULT, SERVO_STOP_DEFAULT, SERVO_STOP_DEFAULT,
  SERVO_STOP_DEFAULT, SERVO_STOP_DEFAULT, SERVO_STOP_DEFAULT,
  SERVO_STOP_DEFAULT, SERVO_STOP_SERVO7, SERVO_STOP_DEFAULT
};

String inputString = "";

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(60);

  pinMode(PUSHER1_ENDSTOP_PIN, INPUT_PULLUP);
  pinMode(PUSHER2_ENDSTOP_PIN, INPUT_PULLUP);

  Serial.println("READY");
}

void loop() {
  checkEndstops();

  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      handleCommand(inputString);
      inputString = "";
    } else {
      inputString += inChar;
    }
  }
}

void checkEndstops() {
  if (digitalRead(PUSHER1_ENDSTOP_PIN) == LOW) pwm.setPWM(2, 0, custom_pwm[2]);
  if (digitalRead(PUSHER2_ENDSTOP_PIN) == LOW) pwm.setPWM(6, 0, custom_pwm[6]);
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  Serial.print("CMD: ");
  Serial.println(cmd);

  if (cmd.startsWith("SET")) {
    int s1 = cmd.indexOf(' ');
    int s2 = cmd.indexOf(' ', s1 + 1);
    int s3 = cmd.indexOf(' ', s2 + 1);
    int servoNum = cmd.substring(s1 + 1, s2).toInt();

    String action;
    int duration = 0;

    if (s3 > 0) {
      action = cmd.substring(s2 + 1, s3);
      duration = cmd.substring(s3 + 1).toInt();
    } else {
      action = cmd.substring(s2 + 1);
    }

    if (action == "FWD") {
      pwm.setPWM(servoNum, 0, 730 - SERVO_PWM_MOVE); // wegduwen
      if (servoNum == 2 || servoNum == 6) {
        delay(duration > 0 ? duration : 500);
        pwm.setPWM(servoNum, 0, custom_pwm[servoNum]);
      }
    }

    else if (action == "REV") {
      if (servoNum == 2 || servoNum == 6) {
        pwm.setPWM(servoNum, 0, SERVO_PWM_MOVE);
        while (true) {
          if ((servoNum == 2 && digitalRead(PUSHER1_ENDSTOP_PIN) == LOW) ||
              (servoNum == 6 && digitalRead(PUSHER2_ENDSTOP_PIN) == LOW)) {
            break;
          }
        }
        pwm.setPWM(servoNum, 0, custom_pwm[servoNum]);
      } else {
        pwm.setPWM(servoNum, 0, SERVO_PWM_MOVE);
      }
    }

    else if (action == "STOP") {
      pwm.setPWM(servoNum, 0, custom_pwm[servoNum]);
    }
  }

  else if (cmd.startsWith("POS")) {
    int s1 = cmd.indexOf(' ');
    int s2 = cmd.indexOf(' ', s1 + 1);
    int servoNum = cmd.substring(s1 + 1, s2).toInt();
    int degrees = cmd.substring(s2 + 1).toInt();
    degrees = constrain(degrees, 0, 210);
    int pulse = map(degrees, 0, 180, POS_MIN, POS_MAX);
    pwm.setPWM(servoNum, 0, pulse);
  }

  else if (cmd.startsWith("CAL")) {
    int s1 = cmd.indexOf(' ');
    int s2 = cmd.indexOf(' ', s1 + 1);
    int servoNum = cmd.substring(s1 + 1, s2).toInt();
    int pwmVal = cmd.substring(s2 + 1).toInt();
    if (pwmVal >= 100 && pwmVal <= 530) {
      custom_pwm[servoNum] = pwmVal;
    }
  }

  else if (cmd.startsWith("ROTATE")) {
    int s1 = cmd.indexOf(' ');
    int s2 = cmd.indexOf(' ', s1 + 1);
    int s3 = cmd.indexOf(' ', s2 + 1);

    int servoNum = cmd.substring(s1 + 1, s2).toInt();
    int degrees = cmd.substring(s2 + 1, s3).toInt();
    String dir = cmd.substring(s3 + 1);

    int timeMs = map(abs(degrees), 0, 360, 0, 1560);
    int pwmVal = SERVO_PWM_MOVE;

    if (dir == "FWD") pwm.setPWM(servoNum, 0, 730 - pwmVal);
    else if (dir == "REV") pwm.setPWM(servoNum, 0, pwmVal);
    else return;

    delay(timeMs);
    pwm.setPWM(servoNum, 0, custom_pwm[servoNum]);
  }

  else if (cmd == "GET ENDSTOPS") {
    bool p1 = (digitalRead(PUSHER1_ENDSTOP_PIN) == LOW);
    bool p2 = (digitalRead(PUSHER2_ENDSTOP_PIN) == LOW);
    Serial.print("ENDSTOP_STATUS ");
    Serial.print(p1 ? "1" : "0");
    Serial.print(" ");
    Serial.println(p2 ? "1" : "0");
  }
}
