import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft

# Read a data file and plot the data
# currently just reads (time,voltage) data from potentiometer example

plt.close('all') # close all plots

# --------------------------------------
# Load and select data
# --------------------------------------
fileName = "/Users/alejandrodiaz/Downloads/test1771356862.csv" # set to your specific filename

# Read csv file
data = pd.read_csv(fileName)

# Extract data from dataframe
t  = np.array(data.Time)
v = np.array(data.voltage)

# Set T1 and T2 to plot data over times of interest
# Plot all data: 
T1,T2 = 0, t[-1]
# or choose specific endpoints as below:
# T1,T2 = 1.05, 3.8
# the next lines determine the index values for your specified times
it1 = np.nonzero(t > T1)[0][0]
it2 = np.nonzero(t < T2)[0][-1]

# create new arrays for values between T1 and T2
T  = t[it1:it2] - t[it1] # Resets time to zero seconds
V = v[it1:it2]

# --------------------------------------
# Plots
# --------------------------------------
# Plot voltage vs time
plt.plot(T,V)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.show()
