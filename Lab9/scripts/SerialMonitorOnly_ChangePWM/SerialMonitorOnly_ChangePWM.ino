// ------------------------------------------------------------------------------------------------------------
// Lab 8: PWM Adjustment Arduino Code
// This code is meant to show output PWM and motor speed in the Serial Monitor only.  No Python code required for operation
// The reference motor speed is determined manually using the serial monitor (a, s, d, z, x, c buttons and pressing Enter)
// ------------------------------------------------------------------------------------------------------------
// NOTE TO STUDENTS: Here is a list of things you will have to adjust
// 1) Your Motor Pin definitions (see Define Motor Pins Section).  Make sure these align with the pin numbers you used when wiring to the digital Arduino pins
// 2) Use the Serial Monitor to manually adjust the PWM output (using a, s, d, z, x, and c buttons)
// 3) Update Serial Monitor to BAUD rate of 19200 to view data
// ------------------------------------------------------------------------------------------------------------
// Use this code to populate a table of PWM value [Int] and corresponding motor speed [rad/s] or [RPM]
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

// Motor Vars
const int offsetA = 1;
Motor motor1 = Motor(AIN1, AIN2, PWMA, offsetA, STBY); // This addresses all relevant pins to the motor output
int motorPwm = 0; // 100 is minimum to overcome stiction in my motor
float PWMout = 255;
float PWM_ratio = 0;
int MotorPwm = motorPwm;

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
float rpm = 0; // Motor speed: Rotations per Minute
float output_rpm = 0; // Output shaft speed: Rotations per Minute
float GR = 45; // Gear ratio

// ----------------------------------------------------------------------------                                                                                                                                                 --------------------------------
// General Variables
// -----------------------------------------------------------------------------------------------------------
float Enval = 0;
float dtval = 0;
volatile long Counter = 0;



// Loop Timing vars
unsigned long timer = 0;    // used to check current time (microseconds)
long loopTime = 500000;       // microseconds
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

  // Setup initial values for timer
  timer = micros();
  previousMillis = timer;

  Serial.println("Motor PWM Adjustments");
  Serial.println("Press a, s, d to increase PWM by 5,10,25, respectively");
  Serial.println("Press z, x, c to decrease PWM by 5,10,25, respectively");
  Serial.println("Press t for reset back to 150");
}

// ------------------------------------------------------------------------------------------------------------
// Begin Loop
// ------------------------------------------------------------------------------------------------------------
void loop() {
 
  unsigned long currT = micros();  // set current time
  currentMillis = currT;
  dt = currentMillis - previousMillis;
  if (dt >= loopTime) {
    // Estimate motor and shaft speed based on number of encoder pulses
    previousMillis = currentMillis;
    Enval = (float) (encoderVal1 + encoderVal2);
    dtval = (float) dt;
    rpm   = 60*Enval*1000000 / (ENC_COUNT_REV*dtval);
    output_rpm = (rpm / GR);

  // Send PWM to motor
  motor1.drive(motorPwm);  
  
  // Outputs
  PWMout = (float) motorPwm;
  PWM_ratio = PWMout/255; // Gives decimal from [-1,1]


  Serial.print("Motor PWM: "); Serial.print(motorPwm); Serial.print(", ");
  Serial.print("dt [us]: "); Serial.print(dt); Serial.print(", ");
  Serial.print(" PULSES: ");  Serial.print(Enval);  Serial.print(", ");
  Serial.print(" MOTOR / Output Shaft [RPM]: "); Serial.print(rpm); Serial.print(" / ");
  Serial.println(output_rpm);

    if (Serial.available())
  {
    char temp = Serial.read();
    if (temp == 'a')
      motorPwm += 5;
    else if (temp == 'z')
      motorPwm -= 5;
    else if (temp == 's')
      motorPwm += 10;
    else if (temp == 'x')
      motorPwm -= 10;
    else if (temp == 'd')
      motorPwm += 25;
    else if (temp == 'c')
      motorPwm -= 25;
    else if (temp == 't')
      motorPwm = 150;  //Reset the PWM to 150
  }

  if (motorPwm > 255)
    motorPwm = 255;
  else if (motorPwm < -255)
    motorPwm = -255;

  

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
