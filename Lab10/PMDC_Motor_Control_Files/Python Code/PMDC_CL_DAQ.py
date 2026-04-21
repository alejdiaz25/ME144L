from ArduinoDAQ import SerialConnect

portName = 'COM4'                      # Communications port name. Make sure it matches port in Arduino IDE
# portName = '/dev/ttyUSB0'
baudRate   = 19200                     # Baud Rate
dataRate   = 20                       # Acquisition data rate (Hz), do not exceed 500
recordTime = 30                        # Number of seconds to record data
numDataPoints = recordTime * dataRate  # Total number of data points to be saved

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
OLgain = 0.65 # [PWM/(rad/s)]

# Closed loop gains
Kp = 0.0    # Determine units     
Ki = 0.0    # Determine units      
Kd = 0.000  # Determine units


#%% Test Cases: Sinusoidal & Step wm reference
# Sinusoidal reference hardcoded in Arduino code
# Step reference set here --> Shows both FF and CL+FF methods

# Commands:
# 'r' : Send data rate
# 'o' : Send OL Gain
# 'P', 'I', 'D' : Send Kp, Ki, and Kd gains, respectively
# 's' : Start sine control Cl
# 'S' : Start sine control OL
# 'k' : Update wm_ref and use OL Control method
# 'c' : Update wm_ref and use CL Control method


# File names for step response
fileName     = 'Data/Lab10_CL_Step_20Hz.csv'
# fileName     = 'Data/Lab10_CL_Step_20Hz_stiction.csv'

# uncomment for step response
commandTimes = [     0,   0,   0,   0,   1,   6,  11,  16,  19,  24,  29] # Time to send command
commandData  = [OLgain,  Kp,  Ki,  Kd,   0, 300, 200,   0, 300, 200,   0] # Value to send over
commandTypes = [   'f', 'P', 'I', 'D', 'k', 'k', 'k', 'k', 'c', 'c', 'k'] # Type of command to send


# uncomment for sine wave
# fileName     = 'Data/Lab10_CL_sine_OL_20Hz.csv'
# commandTimes = [     0,   0,   0,   0,   1,  29] # Time to send command
# commandData  = [OLgain,  Kp,  Ki,  Kd,   0,   0] # Value to send over
# commandTypes = [   'f', 'P', 'I', 'D', 'S', 'k'] # Type of command to send


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
