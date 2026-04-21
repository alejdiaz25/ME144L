"""
LinearRegression_OLgain.py
For ME 144L – DSC Lab
Author: Gabrielle Naquila

Updated: Spring 2026
Comment:
- GN's own Python code for getting OL_gain for Motor PID lab
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression 

PWM = np.array([0, 5, 30, 55, 80, 105, 130, 155, 180, 205, 230, 255])  # [PWM Int];     NOTE: Input your own values
wm  = np.array([0, 0, 0, 550, 960, 1360, 1770, 2200, 2520, 3020, 3440, 3769])  # Motor output [rpm];    NOTE: Input your own values
wm  = 2*np.pi * (wm/60)   # Convert motor output from [rpm] to [rad/s]


# Linear Regression: Get OL_gain by getting the slope and y-int of PWM vs wm 

xdata = wm
ydata = PWM

model = LinearRegression(fit_intercept=False).fit(xdata.reshape(-1,1), ydata)
Rsquared = model.score(xdata.reshape(-1,1), ydata)
slope = model.coef_[0]
intercept = model.intercept_

OL_gain = slope

print('For Motor PID Lab: Finding Open Loop Gain, OL_gain')
print('Open Loop Gain, OL_gain =', OL_gain, '[N·m·s/rad]')
print('R^2 =', Rsquared)
print('y-intercept =', intercept)

#----------

# Plot: w vs wm
plt.figure(1)
plt.scatter(xdata, ydata, c="r", marker='x', label='Raw Data')
plt.plot(xdata, slope*xdata + intercept, label='Linear Fit')
plt.xlabel('Motor Speed ω_m (rad/s)')
plt.ylabel('PWM [int]')
plt.title('wm vs PWM')
plt.legend()
plt.grid()
plt.show()