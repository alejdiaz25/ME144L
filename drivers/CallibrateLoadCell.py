#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 13:23:18 2026

@author: alejandrodiaz
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression 

# NOTE: Raw Data - to be filled in
Mass    = np.array([0, 10, 20, 50, 100])  # [g]
LC_data = np.array([416888, 446004, 475515, 563700, 710520])  # [int]

# Reshape for sklearn (required for X input)
LC_data = LC_data.reshape(-1, 1)

# Fit intercept
FIT = True

# Linear Regression — fit model: X = LC_data, Y = Mass
LCmodel = LinearRegression(fit_intercept=FIT).fit(LC_data, Mass)
R2      = LCmodel.score(LC_data, Mass)
Slope   = float(LCmodel.coef_[0]) # slope m
Intc    = float(LCmodel.intercept_) # y-int b

# NOTE: Try to print fit info below
print(f"y =  {Slope:.6f} + {Intc:.6f}") # Print the linear regression y = mx + b
print(f"R^2 = {R2:.6f}") #printing R2 with 4 decimal places (float)

# Plot
plt.figure()
plt.plot(LC_data, Mass, 'o')  # scatter: raw data
plt.plot(LC_data, Slope * LC_data + Intc)  # regression line
plt.grid()
plt.xlabel('Load Cell Reading [int]')
plt.ylabel('Mass [g]')
plt.legend(["Raw Data", "Regression"])
plt.title('Load Cell Calibration Regression')
plt.show()
