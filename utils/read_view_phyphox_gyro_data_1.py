#-----------------------------------------------------------------
# ME 144L Example code for reading csv file from phyphox (gyro data)
# 1/17/25
# This program assumes sample data file "raw_data_gyro_example.csv" 
# is stored in the same working directory
#-----------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.close('all') # closes any open plots

#-----------------------------------------------------------------
# Read comma-separated values (CSV) file
#-----------------------------------------------------------------
filename  = 'raw_data_gyro_example.csv'
# note: edit the column names
csvdata   = pd.read_csv(filename)
print('Data read...')

#-----------------------------------------------------------------
# Index into the columns using the renamed column header names
#-----------------------------------------------------------------
Tcsv = np.array(csvdata['Time (s)'])
wx   = np.array(csvdata['wx (rad/s)'])
wy   = np.array(csvdata['wy (rad/s)'])
wz   = np.array(csvdata['wz (rad/s)'])
wt   = np.array(csvdata['wt (rad/s)'])

print('Plotting...')

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






