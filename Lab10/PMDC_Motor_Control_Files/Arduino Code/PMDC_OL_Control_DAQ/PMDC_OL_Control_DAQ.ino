// ------------------------------------------------------------------------------------------------------------
// PMDC Motor Control: OL Control Code
// Python code required: PMDC_OL_DAQ.py
// ------------------------------------------------------------------------------------------------------------
// NOTE TO STUDENTS: Here is a list of things you will have to adjust
// 1) Your Motor Pin definitions (see Define Motor Pins Section).  
// Make sure these align with the pin numbers you used when wiring to the digital Arduino pins
// 2) Make sure your Python code BAUD rate is set to same value (19200 for this code)
// ------------------------------------------------------------------------------------------------------------
// This code can be used for Open-Loop gain determination and OL performance experiments
// ------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------
// Include Libraries
// ------------------------------------------------------------------------------------------------------------
#include <Wire.h>
#include <SparkFun_TB6612.h>

// ------------------------------------------------------------------------------------------------------------
// Define Motor Pins
// ------------------------------------------------------------------------------------------------------------
// Motor Pins
#define AIN1 7
#define AIN2 6
#define PWMA 5 // Has tilde on digital output pin
#define STBY 8

// ------------------------------------------------------------------------------------------------------------
// Define Mode enum
// ------------------------------------------------------------------------------------------------------------
enum mode{
  PWM,
  OMEGA_OL,
};

// Motor Vars
const int offsetA = 1;
Motor motor1 = Motor(AIN1, AIN2, PWMA, offsetA, STBY); // This addresses all relevant pins to the motor output
int motorPwm = 0; // 100 is minimum to overcome stiction in my motor
float PWMout = 255;
float PWM_ratio = 0;
int MotorPwm = motorPwm;
float wm_ref = 0.0;
mode controlMode = PWM;
float ol_gain = 0.0;
float w_error = 0.0;

// ------------------------------------------------------------------------------------------------------------
// Encoder variable initialization
// ------------------------------------------------------------------------------------------------------------
// Enc_count_rev: Equals 6 or 3 for CHANGE or RISING/FALLING mode per interrupt; Equals 12 for 2 interrupts on CHANGE mode
#define ENC_COUNT_REV 12 
#define ENC_IN 3
#define ENC2_IN 2
volatile long encoderVal1 = 0;
volatile long encoderVal2 = 0;
long interval = 1;
unsigned long previousMillis = 0;
unsigned long currentMillis = 0;
unsigned long dt = 1000;
float rps = 0; // Motor speed: Rotations per second
float output_rps = 0; // Output shaft speed: Rotations per second
float GR = 45; // Gear ratio

// ------------------------------------------------------------------------------------------------------------
// General Variables
// ------------------------------------------------------------------------------------------------------------
float Enval = 0;
float dtval = 0;
float Tval  = 0;

// Loop Timing vars
unsigned long timer = 0;    // used to check current time (microseconds)
long loopTime = 00000;      // microseconds
bool initLooptime = false;  // boolean to check if loop time has already been set

// ------------------------------------------------------------------------------------------------------------
// Setup
// ------------------------------------------------------------------------------------------------------------
void setup() {
  // initialize serial communications at 115200 bps:
  Wire.begin();
  Serial.begin(19200);

  // Set encoder as input with internal pullup
  pinMode(ENC_IN, INPUT);
  pinMode(ENC2_IN, INPUT);

  // Attach interrupt
  attachInterrupt(digitalPinToInterrupt(ENC_IN), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_IN), updateEncoder2, CHANGE);
}

// ------------------------------------------------------------------------------------------------------------
// Begin Loop
// ------------------------------------------------------------------------------------------------------------
void loop() {

  if (Serial.available() > 0) {       // if data is available
    String str = Serial.readStringUntil('\n');
    readFromPC(str);
  }
  if (initLooptime)
  {
  unsigned long currT = micros();  // set current time
  currentMillis = currT;
  dt = currentMillis - previousMillis; // finds dt in microseconds
  if (dt >= loopTime) {
    // Estimate motor and shaft speed based on number of encoder pulses
    previousMillis = currentMillis;
    Enval = (float) (encoderVal1 + encoderVal2);
    dtval = (float) dt;
    rps   = (float) Enval*1000000.0 / (ENC_COUNT_REV*dtval);
    output_rps = (rps / GR);

  // Step changes in PWM output based on time
  Tval  = (float) currT/1000000.0;

  // Outputs
  float wm = rps*2.0*3.14159;    // [rad/s]

  switch (controlMode)
  {
    case PWM:
      // PWM is already set, do nothing extra
      break;
    case OMEGA_OL:
      motorPwm = ol_gain * wm_ref;
      break;
    default:
      // do nothing
      break;
  }
  
  if (motorPwm > 255) 
    motorPwm = 255;
  else if (motorPwm < -255)
    motorPwm = -255;

  // Send PWM to motor
  motor1.drive(motorPwm);  
  
  // send data over
  sendToPC(&currT);    // Current Time [us]
  sendToPC(&wm_ref);   // Reference motor speed [rad/s]
  sendToPC(&wm);       // Motor Speed [rad/s]
  sendToPC(&motorPwm); // PWM sent to motor [int]

  // Reset encoder value before next loop
  encoderVal1 = 0;
  encoderVal2 = 0;

  }
  }
}

// ------------------------------------------------------------------------------------------------------------
// Update Encoder Function
// ------------------------------------------------------------------------------------------------------------
void updateEncoder()
{
  // Increment value for each pulse from encoder
  encoderVal1++;
}

void updateEncoder2()
{
  // Increment value for each pulse from encoder
  encoderVal2++;
}

void readFromPC(const String input)
{
  int commaIndex = input.indexOf(',');
  char command = input.charAt(commaIndex - 1);
  String data = input.substring(commaIndex + 1);    
  int rate = 0;
  switch(command)
  {
    case 'r':
      // rate command
      rate = data.toInt();
      loopTime = 1000000/rate;         // set loop time in microseconds to 1/frequency sent
      initLooptime = true;             // no longer check for data
      timer = micros();
      break;
    case 'p':
    // PWM command
      motorPwm = data.toInt();
      controlMode = PWM;
      break;
    case 'o':
      // open loop omega
      wm_ref = data.toFloat();
      break;
    case 'f':
      // set open-loop (feedforward) gain
      ol_gain = data.toFloat();
      break;
    case 'k':
      wm_ref = data.toFloat();
      controlMode = OMEGA_OL;
      break;
    default:
    // Otherwise, do nothing
      break;
  
  }

}
// ------------------------------------------------------------------------------------------------------------
// Send Data to PC: Methods to send different types of data to PC
// ------------------------------------------------------------------------------------------------------------

void sendToPC(int* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 2);
}

void sendToPC(float* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}
 
void sendToPC(double* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}

void sendToPC(unsigned long* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}

void sendToPC(long* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}

void sendToPC(volatile long* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}

void sendToPC(char* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 1);
}
