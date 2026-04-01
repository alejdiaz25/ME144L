#
# Flywheel decay - read tachometer sensor data
#
import numpy as np
from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print('Reading and plotting...')
    plt.close('all') # closes any open plots
    filename  = '/Users/alejandrodiaz/Downloads/Lab 2/flywheel_decay_data_noisy.csv'
    csvdata   = pd.read_csv(filename)
    print('Data read...')
    t = np.array(csvdata['Time (sec)'])
    Vtach = np.array(csvdata['Vtach (V)'])

    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    fig, ax1 = plt.subplots()
    ax1.plot(t, Vtach, 'k', label='Vtach')
    ax1.legend(loc="upper right")
    plt.xlabel('Time (sec)')
    plt.tight_layout()
    plt.show()

main()
