#include <Arduino.h>
#include <Servo.h>
// #include <Serial>

// #define DEBUG
#define SER

Servo steering_servo;
Servo speed_servo;
const int STEERING_SERVO_PIN = 2;
const int SPEED_SERVO_PIN = 3;
const int BAUD_RATE = 9600;
const int START_DELAY = 5000;

// Storing state in globals, sue me 
int steer_pos = 0;
int speed_pos = 0;
char steering_state = 's';
char speed_state = 's';

void setup() {
  steering_servo.attach(STEERING_SERVO_PIN);
  speed_servo.attach(SPEED_SERVO_PIN);
  Serial.begin(BAUD_RATE);
  delay(START_DELAY);
}

void loop() {
  #ifdef SER
  /*
  Encoding scheme
  Each incoming message 2 bytes:
    - Byte 0: Desired state of speed
      - 'f' - Forward
      - 'b' - Backward
      - 's' - Stop
    - Byte 1: Desired state of steering
      - 'l' - Left
      - 'r' - Right
      - 's' - Straight
  */
  if (Serial.available()) {
    char recv_msg[3];
    Serial.readBytes(recv_msg, 2);
    recv_msg[2] = '\0';
    steering_state = recv_msg[1];
    speed_state = recv_msg[0];
  } else {
    // Error handling
  }

  steering_servo.write(steer_pos);  
  speed_servo.write(speed_pos);

  switch (speed_state) {
    case 'f': {
      speed_pos = 45;
      break;
    }

    case 'b': {
      speed_pos = 125;
      break;
    }

    case 's': {
      speed_pos = 90;
      break;
    }

    default:
      break;
  }

  switch (steering_state) {
    case 'l': {
      steer_pos = 55;
      break;
    }

    case 'r': {
      steer_pos = 125;
      break;
    }

    case 's': {
      steer_pos = 90;
      break;
    }

    default:
      break;
  }

  #endif

  #ifdef DEBUG
  for (steer_pos = 0; steer_pos <= 180; steer_pos += 1) { 
    // in steps of 1 degree
    steering_servo.write(steer_pos);             
    delay(15);                     
  }
  for (steer_pos = 180; steer_pos >= 0; steer_pos -= 1) {
    steering_servo.write(steer_pos);   
    delay(15);                      
  }
  #endif
}
