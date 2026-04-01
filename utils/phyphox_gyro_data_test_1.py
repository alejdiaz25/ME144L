"""
Created on Wed Jan 21 12:47:30 2026

@author: alejandrodiaz
"""

#-----------------------------------------------------------------
# ME 144L Gyroscope testing data code for reading csv file from phyphox
# 1/21/25
# This program assumes sample data file "Gyroscope_data_test_1.csv" 
# is stored in the same working directory
#-----------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.close('all') # closes any open plots

#-----------------------------------------------------------------
# Read comma-separated values (CSV) file
#-----------------------------------------------------------------
filename  = 'raw_gyro_data_3.csv'
# note: edit the column names
csvdata   = pd.read_csv(filename)
print('Data read...')

#-----------------------------------------------------------------
# Index into the columns using the renamed column header names
#-----------------------------------------------------------------
Tcsv = np.array(csvdata['Time (s)'])
wx   = np.array(csvdata['Gyroscope x (rad/s)'])
wy   = np.array(csvdata['Gyroscope y (rad/s)'])
wz   = np.array(csvdata['Gyroscope z (rad/s)'])
wt   = np.array(csvdata['Absolute (rad/s)'])

print('Plotting...')
print(np.min(wx))

plt.rcParams["figure.figsize"] = [7.00, 7.00]
plt.rcParams["figure.autolayout"] = True
fig, (ax1, ax2, ax3) = plt.subplots(3)
ax1.plot(Tcsv, wx, 'k.', label='wx')
ax1.legend(loc="upper right")
ax1.set_ylabel('wx (rad/s)')
ax2.plot(Tcsv, wy, 'k.', label='wy')
ax2.legend(loc="upper right")
ax2.set_ylabel('wy (rad/s)')
ax3.plot(Tcsv, wz, 'k.', label='wz')
ax3.legend(loc="upper right")
ax3.set_ylabel('wz (rad/s)')
plt.xlabel('Time (sec)')
plt.tight_layout()
plt.show()
# the following can be used to save to *.svg file
# plt.savefig("raw_data_example_plots.svg")