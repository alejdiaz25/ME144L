# Student Edition of PMDC Control - OL Response

# Libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# plt.close('all')

# %% Read CSV File and collect data

#---------------------------
# Import file and read data
# Choose filename based on which Part file you wish to read
#---------------------------
filename     = 'Data/PMDC_OL_Testing_000.csv'          # OL, angular motions, motor only
# (note: you can begin adding additional commented filenames here as they are saved, to record experiments)

data = pd.read_csv(filename)

# dataNames = ['Time', 'wm_ref', 'wm','PWM']
time    = np.array(data.Time)   # [s]
wm_ref  = np.array(data.wm_ref) # [rad/s]
wm_exp  = np.array(data.wm)     # [rad/s]
PWM     = np.array(data.PWM)    # [int]


plt.rcParams["figure.figsize"] = [10,2.5]
plt.rcParams["figure.autolayout"] = True
plt.subplot(1,2,1)
plt.plot(time, wm_ref, label=r'$\omega_{m, ref}$ [rad/s]')
plt.plot(time, wm_exp, label=r'$\omega_m$ [rad/s]')
plt.step(time,PWM,label='PWM [Int]')
plt.title("Raw Data: Motor Speed and PWM output vs Time")
plt.grid()
plt.legend(loc="lower right")
plt.ylabel("Amplitude")
plt.xlabel("Time [s]")

#----------------------------------------------------------------------
# Speed Control Results
# 
# Calculate error and plot over time
# Can use this plot to tabulate error for each wm_ref value
# Remember: wm_ref values are set in DAQ code using variable 'wm_ref_vals'
#----------------------------------------------------------------------

# Calculate Error
wm_error = wm_ref - wm_exp

# Plot Error vs Time
plt.subplot(1,2,2)
plt.plot(time, wm_error, label=r'$\omega_{m}$ error [rad/s]')
plt.step(time,PWM,label='PWM [int]')
plt.title("Speed Control Error and PWM output vs Time")
plt.grid()
plt.legend(loc="lower right")
plt.ylabel("Amplitude")
plt.xlabel("Time [s]")
plt.show()




















