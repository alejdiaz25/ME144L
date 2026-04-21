from ArduinoDAQ import SerialConnect

import math

#portName = 'COM4'                      # Communications port name. Make sure it matches port in Arduino IDE
portName = '/dev/cu.usbserial-DN02BJOA' # redboard @ home
baudRate   = 19200                     # Baud Rate
dataRate   = 20                       # Acquisition data rate (Hz), do not exceed 500

#%% Data lists and Arduino commands
#----------------------------------------------------------------------
# Data to read from Arduino file
# Do not edit anything in this section
#----------------------------------------------------------------------
dataNames = ['Time', 'wm_ref', 'wm','PWM']
dataTypes = [  '=L',     '=f', '=f', '=h']


#%%  Controller Gains
# Update with your own values

# OL Gain
OLgain = 0.7 # [PWM/(rad/s)]

# Commands: (this code only for use with PMCD_OL_Control_DAQ.ino)
# 'r' : Send data rate
# 'o' : Send OL Gain
# 'P', 'I', 'D' : Send Kp, Ki, and Kd gains, respectively
# 'k' : Update wm_ref and use OL Control method


# File names for step response
# Make sure to rename the file when running multiple tests
fileName     = 'Data/PMDC_OL_Testing_00x.csv'

# Estimate time to achieve desired angle
GR = 45
wm_ref = 250 # reference speed in rad/sec
theta_desired_output = 720 # angular rotation in degrees of output shaft
theta_desired = theta_desired_output*GR # motor shaft rotation in degrees
Tinterval = theta_desired*math.pi/180/wm_ref
print(f"Output will rotate by {theta_desired_output:.1f} deg over {Tinterval:.2f} seconds")

# Can now define some times for sending successive commands
# For example, the default program of open loop commands does the following:
# t = 0, the OL gain is sent to Arduino
# t = 0, set OL control and set the wm_ref to 0
# t = T1, set OL control and set to wm_ref
# t = T2, after Tinterval seconds, stop the motor
# t = T3, keep it held for 3 seconds
# t = T4, set OL control and set to wm_ref again

T1 = 1 # turn on run at wm_ref
T2 = T1 + Tinterval # at T3 set wm_ref = 0
T3 = T2 + 3 # after 3 seconds, turn on again at wm_ref
T4 = T3 + Tinterval # turn off after Tinterval seconds
T5 = T4 + 2 # end time for recording; 2 more seconds

# make sure to set the total recordTime and numDataPoints
recordTime = T5                        # Number of seconds to record data
numDataPoints = recordTime * dataRate  # Total number of data points to be saved

# uncomment for step response
commandTimes = [     0,   0,   T1,  T2,  T3, T4] # Time to send command
commandData  = [OLgain,   0, wm_ref, 0, wm_ref, 0] # Value to send over
commandTypes = [   'f',  'k', 'k', 'k', 'k', 'k'] # Type of command to send


#%% Communication with Arduino
#----------------------------------------------------------------------
# Do not edit code below
#----------------------------------------------------------------------
# initializes all required variables
s = SerialConnect(portName, fileName, baudRate, dataRate, \
                  dataNames, dataTypes, commandTimes, commandData, commandTypes)

# Connect to Arduino and send over rate
s.connectToArduino()

# Start Recording Data
print("Recording...")

# Collect data
while len(s.dataStore[0]) < numDataPoints:
    s.getSerialData()
    
    s.sendCommand() # send command to arduino if ready
    
    # Print number of seconds that have passed
    if len(s.dataStore[0]) % dataRate == 0:
        print(len(s.dataStore[0]) /dataRate)   

# Close Arduino connection and save data
s.close()
