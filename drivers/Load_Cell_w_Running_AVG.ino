#include <Wire.h>
#include "SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h"

NAU7802 myScale; //Create instance of the NAU7802 class 

// Running average variable initialization 
#define WINDOW_SIZE 30
long INDEX = 0;
long VALUE = 0;
long SUM = 0;
long AVERAGED = 0;
long READINGS[WINDOW_SIZE];

void setup()
{
  Serial.begin(9600);
  Serial.println("Qwiic Scale Example");

  Wire.begin();

  if (myScale.begin() == false)
  {
    Serial.println("Scale not detected. Please check wiring. Freezing...");
    while (1);
  }
  Serial.println("Scale detected!");
}


void loop()
{  
  if(myScale.available() == true)
  {
    long currentReading = myScale.getReading();

    // Running Average for LC reading
    SUM = SUM - READINGS[INDEX];
    VALUE = currentReading;
    READINGS[INDEX] = VALUE;
    SUM = SUM + VALUE;
    INDEX = (INDEX+1) % WINDOW_SIZE;  
    AVERAGED = SUM / WINDOW_SIZE;
   
    Serial.print("LC [int]: "); Serial.print(currentReading); Serial.print(", ");
    Serial.print("LC AVG [int]: "); Serial.print(AVERAGED);
    Serial.println("");
  }
  delay(200);
}
