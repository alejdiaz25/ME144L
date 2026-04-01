import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

plt.close('all')

filename = 'LoadCell_dynamic_data_2.csv'

data = pd.read_csv(filename)

t = np.array(data.Time)
f = np.array(data.Force) # [counts]

# Select data
T1, T2 = 0, 8
it1 = np.nonzero(t > T1)[0][0]
it2 = np.nonzero(t < T2)[0][-1]
time = t[it1:it2]
f = f[it1:it2]

# enter parameters
m_bungee_g = 10.81 # insert measured mass of bungee cord, kg
cal_slope  = 0.000340 # use your calibration slope
cal_int    = -141.878382 # use your calibration intercept
m_weight = 99.94 * (1/1000) # kg
f_N = ((f*cal_slope + cal_int) - m_bungee_g)/1000.*9.81 # Force in newtons

# Plots
fig, (ax1) = plt.subplots(1)
ax1.plot(time, f_N, label='force_meas')
ax1.grid()
ax1.legend()
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Force [N]')
plt.show()