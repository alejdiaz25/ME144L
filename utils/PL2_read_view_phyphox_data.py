#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 20:41:21 2026

@author: alejandrodiaz
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import scipy.fftpack
from scipy import signal

plt.close('all') # closes any open plots
#-----------------------------------------------------------------
# Read comma-separated values (CSV) file
#-----------------------------------------------------------------
filename = 'raw_data_accelg.csv'
# note: edit the column names
csvdata = pd.read_csv(filename)
print('Data read...')

#-----------------------------------------------------------------
# Index into the columns using the renamed column header names
#-----------------------------------------------------------------
Tcsv = np.array(csvdata['Time (s)'])
accx = np.array(csvdata['Acceleration x (m/s^2)'])
accy = np.array(csvdata['Acceleration y (m/s^2)'])
accz = np.array(csvdata['Acceleration z (m/s^2)'])
acct = np.array(csvdata['Absolute acceleration (m/s^2)'])

# Standard Deviations & Mean

std_x = np.std(accx)
std_y = np.std(accy)
std_z = np.std(accz)
std_t = np.std(acct)

mean_x = np.mean(accx)
mean_y = np.mean(accy)
mean_z = np.mean(accz)
mean_t = np.mean(acct)

#print(std_x)
#print(std_y)
#print(std_z)
#print(std_t)

#print(mean_x)
#print(mean_y)
#print(mean_z)
#print(mean_t)

# spectrum computations
# First, compute the FFT
# this is just for the x-acceleration
acczk = scipy.fftpack.fft(accz)
Nk = len(acczk) # in a FFT only Nk/2 of the points are unique
dt = Tcsv[1]-Tcsv[0] # a way to get the sample time from time array
df = 1/(dt*Nk) # this is the frequency interval
print(f"The frequency spacing is {df} Hz")
# Now, compute the discrete frequency values
fk = [k*df for k in range(Nk//2)]
# compute the magnitude; accxk are complex values
Maccz = [abs(acczk[i]) for i in range(Nk//2)]
# You can now plot Maccx vs. fk
# NOTES:
# If you want the two-sided power-spectral density (PSD):
# Saccx = [(dt/Nk)*abs(accxk[i]) for i in range(Nk//2)]
# multiply by 2 to get the one-sided PSD, Gaccx
# Plot the spectrum (focus on positive frequencies)
'''
plt.figure(figsize=(8, 4))
plt.bar(fk, Maccz, label='Maccz', alpha = 0.5)
plt.title('Frequency Spectrum')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Maccz')
plt.grid()
plt.show()
'''

# 1. Define low-pass G(s): G(s) = 1 / (taut*s + 1))
# where taut = the time constant. For example, for RC circuit,
# taut = R*C, and the cutoff frequency is wc = 1/taut
# The numerator is [1], the denominator is [taut, 1]
R, C = 1, 2 # example numbers
taut = R*C
fc = 1/(2*np.pi*taut) # frequency cut-off in Hz
print(f"Frequency cut-off is {fc} Hz")
# 2. define the CT numerator and denominator
num_c = [1]
den_c = [taut, 1]
# 3. now, create the continuous-time (CT)
# transfer function (TF):
sys_c = signal.TransferFunction(num_c, den_c)
# Assume using the sampling time from data above
# 4. Now, convert to a discrete-time (DT) system
# using the cont2discrete function in scipy.signal package
# note: you can use either 'bilinear' or 'zoh' method
sys_d = signal.cont2discrete((num_c, den_c), dt, method='zoh')
# 5. The following extracts the coefficients and prints them out
b0 = sys_d[0][0][0]
print(f"b0 = {b0}")
b1 = sys_d[0][0][1] # b1
print(f"b1 = {b1}")
a0 = sys_d[1][0]
print(f"a0 = {a0}")
a1 = sys_d[1][1] # a1
print(f"a1 = {a1}")
# end of design part - these coefficients can also
# be used to code up the filter in Arduino
# Now you can implement the digital filter as difference
# equations as follows
# to filter a signal 'x'
# assume you have time vector 't'
xf = np.zeros(len(Tcsv))
xf[0] = accz[0] # need to give it an initial value (pad)
# Now apply the digital filter
# assume you have Nk points in x and t
for k in range(1,Nk):
    xf[k] = -a1*xf[k-1] + b0*accz[k] + b1*accz[k-1]
    
plt.figure(figsize=(8, 4))
plt.plot(Tcsv, accz, label='z (raw)', color='black')
plt.plot(Tcsv, xf, label='z (Filtered)', color='red')
plt.legend()
plt.title('Acceleration (z) with RC filter')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration')
plt.grid()
plt.show()
