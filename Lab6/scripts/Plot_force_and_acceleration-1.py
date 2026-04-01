#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 15:52:23 2026

@author: alejandrodiaz
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

plt.close('all')


filename = 'LoadCellIMU_500g_static4.csv'

data = pd.read_csv(filename)

t = np.array(data.Time)
f = np.array(data.Force) # [counts]
x_a = np.array(data.accX)
y_a = np.array(data.accY)
z_a = np.array(data.accZ)
wx = np.array(data.wx)
wy = np.array(data.wy)
wz = np.array(data.wz)

# Select data
T1, T2 = 0, 8
it1 = np.nonzero(t > T1)[0][0]
it2 = np.nonzero(t < T2)[0][-1]
time = t[it1:it2]
f = f[it1:it2]
z_a = z_a[it1:it2]

# NOTE: Enter parameters
m_bungee_g = 10.81 # insert measured mass of bungee cord, kg
cal_slope  = 0.000340 # use your calibration slope
cal_int    = -141.878382 # use your calibration intercept
m_weight = 99.94 * (1/1000) # kg
f_N = ((f*cal_slope + cal_int) - m_bungee_g)/1000.*9.81 # Force in newtons

# Get acceleration data
acc_coeff = 2*0.061e-3
z_a_ms2 = z_a*acc_coeff* 9.81 # Acceleration in meters/s^2



# Estimate the force due to the mass acceleration
f_acc = -z_a_ms2*m_weight


# Plots
fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)

ax1.plot(time, f_N, label='force_meas')
ax1.plot(time, f_acc, label='force_acc')
ax1.grid()
ax1.legend()
ax1.legend(loc='upper right')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Force [N]')

ax2.plot(time, z_a_ms2, label='acceleration')
ax2.grid()
ax2.legend()
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('acc [m/s^2]')

plt.show()
