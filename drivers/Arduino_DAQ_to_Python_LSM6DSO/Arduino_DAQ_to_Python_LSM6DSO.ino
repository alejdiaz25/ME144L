/* 
 * ------------------------------------------------------------------------------
 * This Arduino sketch sends time data and specified signals to Python
 * Accelerometer usage introduction
 * Spring 2022
 * This program collects both accelerations and angular velocities from an
 * LSM6DS0. The data can be collected using LMS6DS0_PyArduino_DAQ_Driver.py,
 * which saves the data to a *.csv file, or the Serial Monitor or Plotter can be 
 * used by typing 'f,50' to collect values for testing in a free-run mode.
 * The range must be set for acceleration and angular velocity.
 * Currently, it is default to 2g and 
 * Last updated 2/19/22 rgl
 * 
 * NOTES: The data is currently set to be collected in raw integer form. However,
 * examples are shown (commented out) for collecting values in g's or deg/s.
 * ------------------------------------------------------------------------------
*/

#include <Wire.h>              // Must include Wire library for I2C
#include <SparkFunLSM6DSO.h> // 

LSM6DSO myIMU;   // constructor to name the device, access functions

unsigned long timer = 0;    // used to check current time [microseconds]
long loopTime = 0;       // default time between updates, but will be set in python Code [microseconds]
bool initLooptime = false;  // boolean (T/F) to check if loop time has already been set
bool stopProgram = false;

int rawAccX = 0;
int rawAccY = 0;
int rawAccZ = 0;

int rawGyroX = 0;
int rawGyroY = 0;
int rawGyroZ = 0;

void setup() {
  Serial.begin(19200);         // Being serial comms and set Baud rate
  Wire.begin();
  if (myIMU.begin() == false){ // Waits until accelerometer connection is made
    while(1);
  }  
  myIMU.initialize(BASIC_SETTINGS);
  timer = micros();             // start timer
  // set the accelerometer range (2, 4, 8, or 16 g)
  myIMU.setAccelRange(8);
  //myIMU.setAccelRange(4); 
  //myIMU.setAccelRange(8);
  //myIMU.setAccelRange(16);
  // set the gyro range (125, 250 500, 1000, 2000 deg/sec)
  myIMU.setGyroRange(125);
  //myIMU.setGyroRange(250); 
  //myIMU.setGyroRange(500);
  //myIMU.setGyroRange(1000);
  //myIMU.setGyroRange(2000);      
}
 
void loop() {

  if (Serial.available() > 0) {       // if data is available
    String str = Serial.readStringUntil('\n');
    readFromPC(str);
  }
  if (initLooptime && !stopProgram)      // once loop time has been initialized
  {
  
    timeSync(loopTime);   // sync up time to match data rate
    unsigned long currT = micros();  // get current time
    // read accelerations
    rawAccX = myIMU.readRawAccelX();     // get X acceleration raw data (Integer value)
    // can change to read in g (float) 
    // AccX = myIMU.readFloatAccelX();     // get X acceleration in g (float value)
    rawAccY = myIMU.readRawAccelY();     // get Y acceleration raw data (Integer value)
    rawAccZ = myIMU.readRawAccelZ();     // get Z acceleration raw data (Integer value)
    // read gyroscope angular velocities
    rawGyroX = myIMU.readRawGyroX();     // get X gyro raw data (Integer value)
    rawGyroY = myIMU.readRawGyroY();     // get Y gyro raw data (Integer value)
    rawGyroZ = myIMU.readRawGyroZ();     // get Z gyro raw data (Integer value)
        
    // Send data over serial line to computer
    sendToPC(&currT);
    sendToPC(&rawAccX);
    // sendToPC(&AccX); // send floats via serial (check Python reading)
    sendToPC(&rawAccY);
    sendToPC(&rawAccZ);

    sendToPC(&rawGyroX);
    sendToPC(&rawGyroY);
    sendToPC(&rawGyroZ);

  }
  else if (initLooptime && stopProgram)
  {
    // also free run
    // read accelerations
    rawAccX = myIMU.readRawAccelX();     // get X acceleration raw data (Integer value)
    rawAccY = myIMU.readRawAccelY();     // get Y acceleration raw data (Integer value)
    rawAccZ = myIMU.readRawAccelZ();     // get Z acceleration raw data (Integer value)
    // read gyroscope angular velocities
    rawGyroX = myIMU.readRawGyroX();     // get X gyro raw data (Integer value)
    rawGyroY = myIMU.readRawGyroY();     // get Y gyro raw data (Integer value)
    rawGyroZ = myIMU.readRawGyroZ();     // get Z gyro raw data (Integer value)

    // send to serial - free run allows use of Serial Monitor and Plotter
    Serial.print("AccX:");
    Serial.print(myIMU.readFloatAccelX());
    Serial.print(", ");
    Serial.print("AccY:");
    Serial.print(myIMU.readFloatAccelY());
    Serial.print(", ");
    Serial.print("AccZ:");
    Serial.print(myIMU.readFloatAccelZ());
    Serial.print("\n");
    delay(500);

  }

}

/*
 * Timesync calculates the time the arduino needs to wait so it 
 * outputs data at the specified rate
 * Input: deltaT - the data transfer period in microseconds
 */
void timeSync(unsigned long deltaT)
{
  unsigned long currTime = micros();  // get current time
  long timeToDelay = deltaT - (currTime - timer); // calculate how much time to delay for [us]
  
  if (timeToDelay > 5000) // if time to delay is large 
  {
    // Split up delay commands into delay(milliseconds)
    delay(timeToDelay / 1000);

    // and delayMicroseconds(microseconds)
    delayMicroseconds(timeToDelay % 1000);
  }
  else if (timeToDelay > 0) // If time to delay is positive and small
  {
    // Use delayMicroseconds command
    delayMicroseconds(timeToDelay);
  }
  else
  {
      // timeToDelay is negative or zero so don't delay at all
  }
  timer = currTime + timeToDelay;
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
    case 's':
      // stop command
      stopProgram = true;
      break;
    case 'f':
      // free run
      initLooptime = true;
      stopProgram = true;
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
