#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 13:50:06 2026

@author: alejandrodiaz
"""

# ex3_flywheel_decay_analysis.py
# Note: Took out estimated_bias = 0 from Dr. Longoria's code 
# since not necessary for now -GN

#
# Flywheel decay with tachometer sensor simulation
# Results save to csv file on line
#
import numpy as np
from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print('Reading and plotting...')
    plt.close('all') # closes any open plots
    filename  = '/Users/alejandrodiaz/Downloads/flywheel_decay_data_case_1.csv'
    csvdata   = pd.read_csv(filename)
    print('Data read...')
    t = np.array(csvdata['Time (sec)'])
    Vtach = np.array(csvdata['Vtach (V)'])

    # filter
    dt = t[1]-t[0]
    R, C = 1, .05 # example numbers
    tau = R*C
    fc = 1/(2*np.pi*tau)
    print(f"Frequency cut-off is {fc} Hz")
    num_c = [1]
    den_c = [tau, 1]
    # create the continuous-time (CT)
    # transfer function (TF):
    sys_c = signal.TransferFunction(num_c, den_c)

    # Assume using the sampling time from data above

    # Now, convert to a discrete-time (DT) system using a zero-order hold (zoh) method
    # using the cont2discrete function in scipy.signal package
    sys_d = signal.cont2discrete((num_c, den_c), dt, method='zoh')
    #sys_d = sys_c.to_discrete(dt, method='zoh')

    # NOTE: this is the same as using scipy.signal.lti.to_discrete() function

    # print("CT filter system:")
    # print(sys_c)
    # print(f"\nDT system with sampling time {dt} seconds:")
    # print(sys_d)
    # You can also access the numerator and denominator of the discrete system
    # as sys_d[0] and sys_d[1] respectively
    # print(f"\nDiscrete Numerator: {sys_d[0]}")
    # print(f"Discrete Denominator: {sys_d[1]}")
    # print()

    b0 = sys_d[0][0][0]
    print(f"b0 = {b0}")
    b1 = sys_d[0][0][1] # b1
    print(f"b1 = {b1}")
    a0 = sys_d[1][0]
    print(f"a0 = {a0}")
    a1 = sys_d[1][1] # a1
    print(f"a1 = {a1}")

    # now filter voltage
    Vtachf = np.zeros(len(t))
    Vtachf[0] = Vtach[0]
    for k in range(1,len(t)):
        Vtachf[k] = -a1*Vtachf[k-1] + b0*Vtach[k] + b1*Vtach[k-1]

    # Automated level detection
    J = 16.22 # given in kg*m^2
    # can either base it on Vtach or Vtachf
    level_to_find = 0.37*(Vtach[0]) 
    print(f"Level to find: {level_to_find}")

    # indices
    # sampled data (to simulate lower sampling rate)
    n = 25  # consider on every nth point
    t_nth = t[::n]
    print(f"Sampled step = {t_nth[1]} seconds")
    print(f"Sampling frequency is {1/t_nth[1]} Hz")
    Vtach_nth = Vtach[::n]
    crossings = find_level_crossings(Vtach_nth, level_to_find)
    print(Vtach_nth[crossings])
    # print(f"Original Data: {data}")
    print(f"Mean value at level: {np.mean(Vtach_nth[crossings])}")
    tau_mean = np.mean(t_nth[crossings])
    print(f"Mean tau = {tau_mean} sec")
    print(f"Estimated B = {J/tau_mean}")

    # want time values at those crossings to get estimate(s) of tau = J/B
    plt.rcParams["figure.figsize"] = [9.00, 6.00]
    plt.rcParams["figure.autolayout"] = True
    fig, ax1 = plt.subplots()
    ax1.plot(t, Vtach, 'k', label='Vtach')
    ax1.plot(t, Vtachf, 'r:', label='Vtach filtered')
    #ax1.scatter(t_nth,Vtach_nth, color = 'red', marker='o', label='sampled')
    ax1.legend(loc="upper right")
    plt.xlabel('Time (sec)')
    plt.ylabel('Vtach (V)')
    plt.tight_layout()
    plt.show()
    #plt.savefig("Raw_data_1_plots.svg")


# Define some of the subroutines
def find_level_crossings(signal, level=0):
    """
    Finds the indices in a signal array where the value crosses a specified level.
    
    Args:
        signal (list or np.array): The input data series.
        level (int or float): The threshold level to detect crossings.

    Returns:
        np.array: Indices of elements before which a crossing occurs.
    """
    # Compare the signal to the level to get a boolean array
    # Subtracting the level shifts the data so we can look for "zero crossings"
    signs = np.sign(np.array(signal) - level)
    
    # numpy.diff finds the difference between consecutive elements.
    # Where signs change (e.g., from -1 to 1 or 1 to -1), the difference is non-zero.
    # numpy.where returns the indices where this condition is true.
    crossing_indices = np.where(np.diff(signs))[0]
    
    return crossing_indices
main()
