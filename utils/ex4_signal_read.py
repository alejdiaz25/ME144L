#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 14:39:02 2026

@author: alejandrodiaz
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise 4: Signal Filtering and Analysis
"""

import numpy as np
import matplotlib.pyplot as plt

import scipy.fftpack
from scipy import signal

# Data provided in Exercise 4
x = np.array([0,28,9,21,55,36,34,59,
              50,30,55,45,30,30,24,1,
              0,1,-22,-33,-26,-43,-58,-28,
              -49,-71,-41,-51,-59,-21,-16,-26,
              -1,21,8,25,53,40,38,52,
              50,28,54,52,14,30,26,6,
              0,-9,-31,-31,-13,-44,-55,-43,
              -50,-61,-37,-36,-55,-21,-18,20])

# System parameters from text
fs = 64       # Sampling rate (samples/sec)
dt = 1.0/fs     # Time step
t = np.linspace(0, 1, len(x)) # Time vector

# COMPUTE FFT
xk = scipy.fftpack.fft(x)
Nk = len(xk) # in a FFT only Nk/2 of the points are unique
df = 1/(dt*Nk) # this is the frequency interval
print(f"The frequency spacing is {df} Hz")

fk = [k*df for k in range(Nk//2)]
# compute the magnitude; accxk are complex values
Macc = [abs(xk[i]) for i in range(Nk//2)]

plt.figure(figsize=(8, 4))
plt.bar(fk, Macc, label='Macc', alpha = 0.5)
plt.title('Frequency Spectrum')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Macc')
plt.grid()
plt.show()

# LOW PASS RC FILTER
R, C = 1, .05 # example numbers
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
xf = np.zeros(len(t))
xf[0] = x[0] # need to give it an initial value (pad)
# Now apply the digital filter
# assume you have Nk points in x and t
for k in range(1,Nk):
    xf[k] = -a1*xf[k-1] + b0*x[k] + b1*x[k-1]
    
plt.figure(figsize=(8, 4))
plt.plot(t, x, 'bo', label='z (raw)')
plt.plot(t, xf, label='z (Filtered)', color='red')
plt.legend()
plt.title('Acceleration (z) with RC filter')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration')
plt.grid()
plt.show()
