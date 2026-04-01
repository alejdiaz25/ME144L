"""
Read_Plot_wLog_Decrement_student.py

For Lab 4 Exercise 5
Author: GN

Updated: Spring 2026
Comment: Adjusted for student version 


Description:
------------
This script processes accelerometer data collected from a cantilever beam experiment.
It performs peak detection and dynamic analysis to estimate the following properties:

1. Extracts vertical acceleration data (accZ) from a CSV file.
2. Detects peaks in the acceleration signal to analyze oscillatory motion.
3. Computes the logarithmic decrement (δ) based on exponential decay of peak amplitudes.
4. Estimates the damping ratio (ζ) from δ.
5. Calculates the damped period (Td) from time differences between successive peaks.
6. Computes the damped natural frequency (ω_d) and undamped natural frequency (ω_n).
7. Models the beam as a single-degree-of-freedom (SDOF) spring-mass oscillator using:
    - Beam geometry and material properties to compute effective stiffness (k)
    - The estimated ω_n to solve for effective mass (m_eff) at the beam tip.

Outputs:
--------
- Peak amplitudes and times
- Logarithmic decrement (δ)
- Damping ratio (ζ)
- Damped period (Td)
- Natural frequencies (ω_d, ω_n) in rad/s and Hz
- Effective stiffness (k) and effective mass (m_eff) based on beam theory

"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import find_peaks

# ------------------- Reading ang plotting original Acc Z signal -------------------

plt.close('all')

filename = 'test1771963952.csv' #Deflection file

data = pd.read_csv(filename)

time = np.array(data.Time)
z = np.array(data.accZ) # [counts]
wz = np.array(data.wz)  # [counts]

# convert counts to gs
conv_accel =  0.244e-3 # g range; convert from int to float in [g]
# NOTE: 0.061 for 2g, 0.122 for 4g, 0.244 for 8g, 0.488 for 16g
accz_g = conv_accel*z  # [g]


plt.figure(figsize=(12,5))
plt.plot(time, accz_g, label='z')
plt.grid()
plt.legend()
plt.xlabel('Time [s]')
plt.ylabel("Acceleration [g]")
plt.title("Acceleration vs Time")

# ------------------- Finding accz_g signal peaks -------------------

# Find peaks in accz_g 
peaks_indices, _ = find_peaks(accz_g, prominence=0.01)

# Extract peak times and values
peak_times = time[peaks_indices]
peak_vals = accz_g[peaks_indices]

# Plot original accz_g signal with peaks 
plt.figure(figsize=(12,5))
plt.plot(time, accz_g, label='accZ [g]')
plt.plot(peak_times, peak_vals, 'ro', label='Detected Peaks')
plt.grid()
plt.xlabel('Time [s]')
plt.ylabel('Acceleration [g]')
plt.title('Peaks in accZ signal')
plt.legend()
plt.show()

# Print peak values 
for i, (t, val) in enumerate(zip(peak_times, peak_vals)):
    print(f"Peak {i+1}: Time = {t:.3f} s, Value = {val:.3f} g")


# ------------------- Plotting ln(A0 / An) vs n with linear fit -------------------


# Find the global maximum peak
idx_max = np.argmax(peak_vals)
global_peak_idx = peaks_indices[idx_max]
A0 = accz_g[global_peak_idx]

# Print value of largest peak
print(f"Largest peak A0 = {A0:.4f} g at index {global_peak_idx}, time = {time[global_peak_idx]:.4f} s")

# Trim accz_g and time from the global peak onward
accz_trimmed = accz_g[global_peak_idx:]
time_trimmed = time[global_peak_idx:]


# Detect new peaks on trimmed signal
peaks_trimmed, _ = find_peaks(accz_trimmed, prominence=0.01)
peak_vals_trimmed = accz_trimmed[peaks_trimmed]

# Use A0 from the trimmed signal
A0_new = peak_vals_trimmed[0]
n_vals = np.arange(len(peak_vals_trimmed))
log_ratios = np.log(A0_new / peak_vals_trimmed)


# ------------------- Getting the slope of ln(A0 / An) vs n -------------------

# Linear fit: ln(A0 / An) = Beta * n
coeffs = np.polyfit(n_vals, log_ratios, 1) # gets slope and yint [m,y-int] = [beta,y-int]
beta_fit = coeffs[0] 

print(f"Estimated logarithmic decrement (from line fit) β = {beta_fit:.4f}")

# Plot ln(A0 / An) vs n with linear fit
fit_line = np.polyval(coeffs, n_vals)
plt.figure()
plt.plot(n_vals, log_ratios, 'b-', label='ln(A0 / An)')
plt.plot(n_vals, fit_line, 'r--', label=f'Linear fit: β ≈ {beta_fit:.4f}')
plt.xlabel('Peak Number n')
plt.ylabel('ln(A0 / An)')
plt.title('Logarithmic Decrement and Linear Fit')
plt.grid(True)
plt.legend()
plt.show()

# ------------------- Getting damping ratio zeta ζ  -------------------

beta = beta_fit  

# NOTE: Calculate zeta given damping ratio is beta.
#       Use np.sqrt() for square root
zeta = (beta ** 2) / (np.sqrt(4*(np.pi**2) + beta ** 2))

print(f"Estimated damping ratio ζ  = {zeta:.6f}")


# ------------------- Estimate damped period Td from peak times -------------------

peak_times_trimmed = time_trimmed[peaks_trimmed]
periods = np.diff(peak_times_trimmed)
Td = np.mean(periods)

print(f"Estimated damped period Td = {Td:.6f} s")


# ------------------- Compute damped and undamped natural frequencies -------------------

# NOTE: Calculate the damped natural frequency (rad/s) given damped period is Td
omega_d = 2 * np.pi / Td  # [rad/s]

# NOTE: Calculate the undamped natural frequency given omega_d and zeta 
omega_n = omega_d / np.sqrt(1 - zeta)

# Convert to Hz (optional)
f_d = omega_d / (2 * np.pi)  # [Hz]
f_n = omega_n / (2 * np.pi)  # [Hz]

print(f"Damped natural frequency ω_d = {omega_d:.6f} rad/s (f_d = {f_d:.4f} Hz)")
print(f"Undamped natural frequency ω_n = {omega_n:.6f} rad/s (f_n = {f_n:.4f} Hz)")


# ------------------- Compute Effective Mass m_eff of Cantilever Beam -------------------


# NOTE: Change the width, thickness, and length below
# Beam dimensions and Young's modulus 
width     = 1.00 * 0.0254    # m
thickness = 0.125 * 0.0254   # m
length    = 40 * 0.01        # cm to m; length from table
E = 68.9e9  # Young's Modulus for 6061 Aluminum [Pa]


# NOTE: Calculate effective mass from ω_n
I =  (1/12) * width * thickness ** 3  # Moment of inertia for rectangular cross-section [m^4] 
k =  (3 * E * I ) / (length ** 3)# Effective stiffness at cantilever tip [N/m]
rho = 2700
m_beam = width * thickness * length * rho
m_mass = 60 * 0.001 
m_eff = m_mass + 0.23 * m_beam # [kg]
omega_n_theory = np.sqrt(k/m_eff)

m_eff_theory = k/(omega_n_theory ** 2)

print(f"Beam dimensions: width = {width:.4f} m, thickness = {thickness:.4f} m, length = {length:.4f} m")
print(f"Moment of inertia I = {I:.4e} m⁴")
print(f"Stiffness k = {k:.2f} N/m")
print(f"Estimated effective mass m_eff = {m_eff:.6f} kg")

print(omega_n_theory)
print(m_eff_theory)
