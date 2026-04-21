// ------------------------------------------------------------------------------------------------------------
// PMDC Motor Speed Control Arduino Code
// This code is meant to show OL and CL control in the Serial Monitor only.  No Python code required
// The reference motor speed is determined manually using the serial monitor (a, s, z, x buttons adjust wm_ref)
// ------------------------------------------------------------------------------------------------------------
// NOTE TO STUDENTS: Here is a list of things you will have to adjust
// 1) Your Motor Pin definitions (see Define Motor Pins Section).  Make sure these align with the pin numbers you used when wiring to the digital Arduino pins
// 2) The Open-Loop gain and the Closed-Loop PID gains (see OL & CL Control Gains Section)
// 3) Uncomment the desired method of control (see Motor Control Scheme Section within the Arduino loop)
// ------------------------------------------------------------------------------------------------------------
// Use this code to assess OL and CL control performance; also iterate PID gain values
// ------------------------------------------------------------------------------------------------------------


// ------------------------------------------------------------------------------------------------------------
// Include Libraries
// ------------------------------------------------------------------------------------------------------------
#include <Wire.h>
#include <SparkFun_TB6612.h>

// ------------------------------------------------------------------------------------------------------------
// Define Motor Pins
// ***DOUBLE CHECK ALL PIN NUMBERS MATCH YOUR OWN CIRCUIT CONNECTIONS***
// ------------------------------------------------------------------------------------------------------------
// Motor Pins
#define AIN1 7
#define AIN2 6
#define PWMA 5 // Has tilde on digital output pin
#define STBY 8

// ------------------------------------------------------------------------------------------------------------
// Motor Vars
// ------------------------------------------------------------------------------------------------------------
const int offsetA = 1;
Motor motor1 = Motor(AIN1, AIN2, PWMA, offsetA, STBY); // This addresses all relevant pins to the motor output
int motorPwm = 150; // 140 is minimum to overcome stiction in my motor
float PWMout = 255;
float PWM_ratio = 0;
int MotorPwm = motorPwm;

// ------------------------------------------------------------------------------------------------------------
// Running average variable initialization
// ------------------------------------------------------------------------------------------------------------
#define WINDOW_SIZE 20
int INDEX    = 0;
int VALUE    = 0;
int SUM      = 0;
int AVERAGED = 0;
int READINGS[WINDOW_SIZE];

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
float rps = 0; // Motor speed: Rotations per Second
float output_rps = 0; // Output shaft speed: Rotations per Second
float GR = 45; // Gear ratio

// ------------------------------------------------------------------------------------------------------------
// General Variables
// ------------------------------------------------------------------------------------------------------------
float Vbus   = 5;
float Vin    = 0;
float Enval  = 0;
float dtval  = 0;
float Tval   = 0;
float wm     = 0;

// Loop Timing vars
unsigned long timer = 0;    // used to check current time (microseconds)
long loopTime = 50000;      // microseconds (For 20 Hz, set to 50000)
bool initLooptime = false;  // boolean to check if loop time has already been set

// ------------------------------------------------------------------------------------------------------------
// OL & CL Control Variables
// ------------------------------------------------------------------------------------------------------------
float wm_ref  = 0;  // [rad/s], Allowable Range: 205 <= wm_ref <= 400 [rad/s] for my 5V input
float w_error = 0;  // [rad/s]
float OL_PWM, CL_PWM, CL_FF_PWM; 
float edt   = 0;    // Current integral error value
float esum  = 0;    // Running summation of integral error
float dedt  = 0;    // Derivative error
float elast = 0;    // Last step error

// ------------------------------------------------------------------------------------------------------------
// OL & CL Control Gains
// You will adjust these gains based on experimental testing results
// ------------------------------------------------------------------------------------------------------------
float OL_gain = 0.5; // Solve for units
float kp = 0.10;      // Solve for units, adjust with 0.1 increments
float ki = 0.00;      // Solve for units, adjust with 0.1 increments
float kd = 0.000;     // Solve for units, start very small here (e.g., kd = 0.001), adjust with 0.001 increments

// Min PWM to rotate motor
int PWMbase = 150;  // Base PWM signal to move motor
float c1    = 0;    // Multiplier for PWMbase (0 = Off; 1 = On)

// ------------------------------------------------------------------------------------------------------------
// Setup
// ------------------------------------------------------------------------------------------------------------
void setup() {
  // initialize serial communications at 19200 bps:
  Wire.begin();
  Serial.begin(19200);

  // Set encoder as input with internal pullup
  pinMode(ENC_IN, INPUT);
  pinMode(ENC2_IN, INPUT);

  // Attach interrupt
  attachInterrupt(digitalPinToInterrupt(ENC_IN), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_IN), updateEncoder2, CHANGE);

  // Setup initial values for timer
  timer = micros();
  previousMillis = timer;

  //Serial.println("Motor Speed (wm) Adjustments");
  //Serial.println("Press a, s to increase wm by 5,10, respectively");
  //Serial.println("Press z, x to decrease wm by 5,10, respectively");
  //Serial.println("Press t for jump to 300 [rad/s]");
  //Serial.println("Press o to reset at   0 [rad/s]");
}

// ------------------------------------------------------------------------------------------------------------
// Begin Loop
// ------------------------------------------------------------------------------------------------------------
void loop() {
 
  unsigned long currT = micros();  // set current time
  currentMillis = currT;
  dt = currentMillis - previousMillis;

  // Begin control/measurement loop when loopTime has elapsed
  if (dt >= loopTime) {
    // Estimate motor and shaft speed based on number of encoder pulses
    previousMillis = currentMillis;
    Enval = (float) (encoderVal1 + encoderVal2);
    dtval = (float) dt;
    rps   = (float) Enval*1000000.0 / (ENC_COUNT_REV*dtval);
    output_rps = (rps / GR);

  // Calculate Error in motor speed
  wm  = rps*2*3.14159; // [rad/s]
  if (wm_ref == 0){
    w_error = 0;
    edt     = 0;
    esum    = 0;
    dedt    = 0;
    c1      = 0;
    elast   = 0;}
  else{
    w_error = wm_ref - wm;   // [rad/s]
    edt     = esum + w_error*dtval/1000000;
    esum    = edt; // Save current error summation for next iteration
    dedt    = (w_error - elast)/(dtval/1000000);
    c1      = 1;
    elast   = w_error;
  }


  // Calculate Control Output
  OL_PWM    = wm_ref*OL_gain;                          // OL (Feedforward) Control Law
  CL_PWM    = kp*w_error + ki*edt + kd*dedt + c1*PWMbase; // CL Control Law (with PWM base value required to move the motor; my PWMbase = 140)
  CL_FF_PWM = OL_PWM + CL_PWM - c1*PWMbase;               // CL Control Law w FF (subtract out PWM base value)

  // ----------------------------------------------------------------------------------------------------------------------------------------------------
  // Motor Control Scheme:
  // ***Uncomment desired control method below***
  // ----------------------------------------------------------------------------------------------------------------------------------------------------
  // Round float value to integer (Note: using (int)(...) is the same as using the floor() function; round() prevents truncation)
   motorPwm = round(OL_PWM);    // Uncomment for OL Control only
  // motorPwm = round(CL_PWM);    // Uncomment for CL Control only
  // motorPwm = round(CL_FF_PWM); // Uncomment for OL+CL Control (Called CL control with Feedforward)
  // ----------------------------------------------------------------------------------------------------------------------------------------------------

  // Saturate motor PWM output
  if (motorPwm > 255){
    motorPwm = 255;}
  else if (motorPwm < -255){
    motorPwm = -255;}
  motor1.drive(motorPwm);  

  // Print to serial monitor
  Serial.print("Wmref:"); Serial.print(wm_ref); Serial.print(", ");
  Serial.print("Wmexp:"); Serial.print(wm);     Serial.print(", ");  
  Serial.print("PWM:");   Serial.print(motorPwm); Serial.print(", ");
  Serial.print("Wmerror:"); Serial.print(w_error); 
  Serial.println();

  
  // Code to adjust reference motor speed
    if (Serial.available())
  {
    char temp = Serial.read();
    if (temp == '+' || temp == 'a')
      wm_ref += 5;
    else if (temp == '-' || temp == 'z')
      wm_ref -= 5;
    else if (temp == 's')
      wm_ref += 10;
    else if (temp == 'x')
      wm_ref -= 10;
    else if (temp == 't')
      wm_ref = 300;  //Jump to 300 [rad/s]
    else if (temp == 'o')
      wm_ref = 0;    //Reset to 0 [rad/s]
  }

  // Reset encoder value before next loop
  encoderVal1 = 0;
  encoderVal2 = 0;

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
