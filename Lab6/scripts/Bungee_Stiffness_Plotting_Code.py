#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 15:42:12 2026

@author: alejandrodiaz
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# NOTE: Enter your measurements here:
LC_readings = np.array([507386, 1357956, 1600443, 1748936, 1887860, 2002329, 
                        2116206, 2183967, 2314433, 2366345, 2484102, 2566164, 
                        2647827]) #int readings
stretch_data = np.array([0,10,20,30,40,50,60,70,80,90,100,110,120]) # in mm

stretch_data = stretch_data * 1e-3  # convert to meters

stretch_data = stretch_data[0:3]
LC_readings = LC_readings[0:3]
# Calibration equation from your linear fit
# y = 0.000340 * x - 141.878382
force_data = (0.000340 * LC_readings - 141.878382) * (9.81/1000) # NOTE: Enter your linear regression equation

#  RESHAPE for sklearn
stretch_data = stretch_data.reshape(-1, 1)

# LINEAR REGRESSION 
model = LinearRegression()
model.fit(stretch_data, force_data)

slope = float(model.coef_[0])
intercept = float(model.intercept_)
r_squared = model.score(stretch_data, force_data)

print(slope)
print(intercept)
print(r_squared)

# PLOT 
plt.figure()
plt.plot(stretch_data, force_data, 'o', label='Measured Data')
plt.grid(True)
plt.xlabel('Bungee Stretch (m)')
plt.ylabel('Force (N)')
plt.title('Bungee Cord Stiffness: Force vs. Stretch')
plt.legend()
plt.tight_layout()
plt.show()