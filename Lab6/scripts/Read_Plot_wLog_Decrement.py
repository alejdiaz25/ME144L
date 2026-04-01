"""
Read_Plot_wLog_Decrement.py

For Lab 6 Exercise 3 / 4
Author: Alejandro Diaz
Adapted from: GN (Spring 2026)

Description:
------------
This script processes load cell force data collected from a bungee cord 
oscillation experiment. It performs peak detection and dynamic analysis 
to estimate the following system properties:

1. Reads and converts raw load cell counts to force [N] using a calibration equation.
2. Subtracts the static equilibrium offset to obtain a zero-mean force signal.
3. Detects peaks in the oscillatory force signal.
4. Computes the logarithmic decrement (β) based on exponential decay of peak amplitudes.
5. Estimates the damping ratio (ζ) from β.
6. Calculates the damped period (Td) from time differences between successive peaks.
7. Computes the damped natural frequency (ω_d) and undamped natural frequency (ω_n).
8. Back-calculates the effective spring stiffness (k) from ω_n and the known hanging mass.

Outputs:
--------
- Calibrated force vs. time plot
- Zero-mean force with detected peaks
- Logarithmic decrement plot with linear fit
- Logarithmic decrement (β)
- Damping ratio (ζ)
- Damped period (Td)
- Natural frequencies (ω_d, ω_n) in rad/s and Hz
- Effective spring stiffness (k)

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

plt.close('all')

# ------------------- Load Data -------------------

filename = 'LoadCell_dynamic_data_2.csv'  # NOTE: Change to your dynamic oscillation file

data = pd.read_csv(filename)

t = np.array(data.Time)
f_counts = np.array(data.Force)  # [int counts]

# ------------------- Calibration Parameters -------------------

# NOTE: Enter your calibration slope and intercept from Exercise 2
cal_slope = 0.000340        # [g / count]
cal_int   = -141.878382     # [g]

# NOTE: Enter the measured mass of the bungee cord tare [g]
m_bungee_g = 10.81          # [g]

# NOTE: Enter the mass of the hanging weight [kg]
m_weight = 99.94 * (1/1000) # [kg]

# ------------------- Convert Counts to Force [N] -------------------

# Subtract tare, convert g -> kg -> N
f_N = ((f_counts * cal_slope + cal_int) - m_bungee_g) / 1000.0 * 9.81

# ------------------- Select Time Window -------------------

# NOTE: Adjust T1 and T2 to isolate the oscillation region of interest
T1, T2 = 0.0, 8.0
it1 = np.nonzero(t > T1)[0][0]
it2 = np.nonzero(t < T2)[0][-1]
time  = t[it1:it2]
f_N   = f_N[it1:it2]

# ------------------- Plot Calibrated Force vs. Time -------------------

plt.figure(figsize=(12, 5))
plt.plot(time, f_N, label='Measured Force')
plt.grid(True)
plt.xlabel('Time [s]')
plt.ylabel('Force [N]')
plt.title('Calibrated Force vs. Time')
plt.legend()

# ------------------- Zero-Mean Force Signal -------------------

# Use the tail of the signal (steady state) as the equilibrium reference
f_mean  = f_N[-500:].mean()
f_zm    = f_N - f_mean

print(f"Static equilibrium force = {f_mean:.4f} N  (expected: m*g = {m_weight*9.81:.4f} N)")

# ------------------- Peak Detection -------------------

# NOTE: Adjust prominence threshold if too many or too few peaks are detected
peaks_indices, _ = find_peaks(f_zm, prominence=0.01, height=0.01, distance=5)

peak_times = time[peaks_indices]
peak_vals  = f_zm[peaks_indices]

# Keep only positive peaks
pos_mask    = peak_vals > 0
peaks_indices = peaks_indices[pos_mask]
peak_times  = peak_times[pos_mask]

# Plot zero-mean force with detected peaks
plt.figure(figsize=(12, 5))
plt.plot(time, f_zm, label='Zero-Mean Force [N]')
plt.plot(peak_times, peak_vals, 'ro', label='Detected Peaks')
plt.grid(True)
plt.xlabel('Time [s]')
plt.ylabel('Force [N]')
plt.title('Zero-Mean Force with Detected Peaks')
plt.legend()

# Print peak values
for i, (pt, pv) in enumerate(zip(peak_times, peak_vals)):
    print(f"Peak {i+1}: Time = {pt:.3f} s, Amplitude = {pv:.4f} N")

# ------------------- Trim to Global Maximum Peak -------------------

idx_max        = np.argmax(peak_vals)
A0             = peak_vals[idx_max]
trim_start_idx = peaks_indices[idx_max]

print(f"\nLargest peak A0 = {A0:.4f} N at time = {time[trim_start_idx]:.4f} s")

# Trim signal from the global peak onward
f_zm_trimmed   = f_zm[trim_start_idx:]
time_trimmed   = time[trim_start_idx:]

# Detect peaks on trimmed signal
peaks_trimmed, _ = find_peaks(f_zm_trimmed, prominence=0.01, height=0.01, distance=5)
peak_vals_trimmed = f_zm_trimmed[peaks_trimmed]
peak_times_trimmed = time_trimmed[peaks_trimmed]

# Keep positive peaks only
pos_mask_trim     = peak_vals_trimmed > 0
peaks_trimmed     = peaks_trimmed[pos_mask_trim]
peak_vals_trimmed = peak_vals_trimmed[pos_mask_trim]
peak_times_trimmed = peak_times_trimmed[pos_mask_trim]

# ------------------- Logarithmic Decrement -------------------

A0_new     = peak_vals_trimmed[0]
n_vals     = np.arange(len(peak_vals_trimmed))
log_ratios = np.log(A0_new / peak_vals_trimmed)

# ------------------- Linear Fit for β -------------------

# Linear fit: ln(A0 / An) = β * n
coeffs   = np.polyfit(n_vals, log_ratios, 1)  # [slope=β, y-intercept]
beta_fit = coeffs[0]

print(f"\nEstimated logarithmic decrement (slope) β = {beta_fit:.4f}")

# Plot ln(A0 / An) vs n
fit_line = np.polyval(coeffs, n_vals)
plt.figure()
plt.plot(n_vals, log_ratios, 'b-o', markersize=4, label='ln(A0 / An)')
plt.plot(n_vals, fit_line, 'r--', label=f'Linear fit: β ≈ {beta_fit:.4f}')
plt.xlabel('Peak Number n')
plt.ylabel('ln(A₀ / Aₙ)')
plt.title('Logarithmic Decrement and Linear Fit')
plt.grid(True)
plt.legend()

# ------------------- Damping Ratio ζ -------------------

beta = beta_fit

# NOTE: Solve for zeta from the logarithmic decrement relation:
#       β = 2π·ζ / sqrt(1 - ζ²)  =>  ζ = β / sqrt(4π² + β²)
zeta = beta / (np.sqrt(4 * (np.pi ** 2) + beta ** 2))

print(f"Estimated damping ratio ζ = {zeta:.6f}")

# ------------------- Damped Period Td -------------------

periods = np.diff(peak_times_trimmed)
Td      = np.mean(periods)

print(f"Estimated damped period Td = {Td:.6f} s")

# ------------------- Natural Frequencies -------------------

# Damped natural frequency [rad/s]
omega_d = 2 * np.pi / Td

# Undamped natural frequency [rad/s]
# NOTE: omega_n = omega_d / sqrt(1 - zeta^2)
omega_n = omega_d / np.sqrt(1 - zeta ** 2)

f_d = omega_d / (2 * np.pi)  # [Hz]
f_n = omega_n / (2 * np.pi)  # [Hz]

print(f"Damped natural frequency   ω_d = {omega_d:.4f} rad/s  (f_d = {f_d:.4f} Hz)")
print(f"Undamped natural frequency ω_n = {omega_n:.4f} rad/s  (f_n = {f_n:.4f} Hz)")

# ------------------- Back-Calculate Spring Stiffness -------------------

# Model the system as a SDOF spring-mass: ω_n² = k / m
# NOTE: m_weight is the hanging mass [kg]; bungee cord mass is neglected here
k_eff = omega_n ** 2 * m_weight

print(f"\nBack-calculated spring stiffness k = ω_n² · m = {k_eff:.4f} N/m")

from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(n_vals, log_ratios)
print(f"R² = {r_value**2:.6f}")

print(f"(Compare to static bungee stiffness measured in Exercise 3)")

plt.show()
