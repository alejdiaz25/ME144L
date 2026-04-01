int LDR_pin = 0;
int POT_pin = 1;
int Switch_pin = 3;
int Output_pin = 2;
bool switchState;
int LDRValue, POTValue, outputValue;

void setup()
{
 
  pinMode(Switch_pin, INPUT);
  pinMode(Output_pin, OUTPUT);
  Serial.begin(38400);
  
}

void loop()
{
  // read the state of the switch value:
  bool switchState = digitalRead(Switch_pin);
    
  if (switchState == HIGH) 
  {
    // turn Automatic light:
    // read the analog in value:
    LDRValue = analogRead(LDR_pin);
    // map it to the range of the analog out:
    outputValue = map(LDRValue, 0, 1023, 0, 255);
    // change the analog out value:
    analogWrite(Output_pin, outputValue);
    
    // print the results to the Serial Monitor:
    Serial.print("Automatic Swtich: ");
    Serial.print("sensor = ");
    Serial.print(LDRValue);
    Serial.print("\t output = ");
    Serial.println(outputValue);
  } 
  else 
  {
    // turn Manual Light:
    // read the analog in value:
    POTValue = analogRead(POT_pin);
    // map it to the range of the analog out:
    outputValue = map(POTValue, 0, 1023, 0, 255);
    // change the analog out value:
    analogWrite(Output_pin, outputValue);
    
    // print the results to the Serial Monitor:
    Serial.print("Manual Swtich: ");
    Serial.print("sensor = ");
    Serial.print(POTValue);
    Serial.print("\t output = ");
    Serial.println(outputValue);
  }
 }
