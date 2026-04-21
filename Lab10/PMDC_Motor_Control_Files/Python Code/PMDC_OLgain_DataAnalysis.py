# Student Edition of PMDC Motor Control
# OL Gain Determination

# Libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression 

plt.close('all')

#%% Section: Open-Loop Gain Determination
#----------------------------------------------------------------------
# Input your PWM and wm values from last week's step tests to determine your OL Gain
#----------------------------------------------------------------------
PWM = np.array([160, 180, 200, 220, 240, 255]) # [PWM Int]
wm  = np.array([0, 0, 0, 0, 0, 0]) # [rad/s]

#---------
# Linear Regressions for OL Gain
#---------
wmval = wm.reshape(-1,1)
model = LinearRegression(fit_intercept=False).fit(wmval, PWM)
R2    = model.score(wmval, PWM)
OLgain, intc1 = float(model.coef_), float(model.intercept_)
print('OL Gain [PWM/(rad/s)]:', OLgain)
print('OL intercept [PWM]:', intc1)
print('OL Gain R^2:', R2)

# Plot regression vs raw data
plt.figure()
plt.plot(wm, PWM, '-o', label='PWM')
plt.plot(wm, OLgain*wm + intc1, '--', label='OL Regression')
plt.title("Motor PWM vs Motor Speed")
plt.grid()
plt.legend()
plt.ylabel("PWM [Int]")
plt.xlabel("$\omega_m$ [rad/s]")
plt.axis([0, wm[-1]+20, 0, PWM[-1]+20])
plt.show()





















