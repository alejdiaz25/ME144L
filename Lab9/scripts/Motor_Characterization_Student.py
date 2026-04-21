#!/opt/anaconda3/bin/python3
"""
Motor_Characterization_Student.py

For ME 144L - DSC Lab
Author: Gabrielle Naquila (template), filled in by Alejandro Diaz

Updated: Spring 2026

Description:
This script processes experimental motor data to estimate key motor parameters
using linear regression and basic DC motor relationships.

Outputs:
- Motor constant (rm) [V*s/rad == N*m/A]
- Rotational damping (Bm) [N*m*s/rad]
- Coulomb friction (Tcf) [N*m]
- R^2 for each regression
- Plots saved to ../figures/:
    1. vm_vs_wm.png            -- Back EMF vs motor speed
    2. tm_vs_wm.png            -- Motor torque vs motor speed
    3. torque_speed_family.png -- Modeled output torque-speed curves at multiple Vin
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# Resolve a figures directory next to this script's parent (Lab9/figures/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures"))
os.makedirs(FIG_DIR, exist_ok=True)


# %%--------------------------------------------------------------------------
# Step 0: Gear Ratio
GR = 45     # Gear Ratio [unitless]

print('Step 0: Take note of Gear Ratio below')
print('Gear Ratio, GR =', GR)
print()


# %%--------------------------------------------------------------------------
# Step 1: Armature Resistance, Rm  (measured at motor terminals with a DMM)
Rm = 26.9   # [Ohm]

print('Step 1: Finding Armature Resistance, Rm')
print('Armature resistance, Rm =', Rm, '[Ohm]')
print()


# %%--------------------------------------------------------------------------
# Step 2: Motor constant, rm
print('Step 2: Finding motor constant, rm')

Vsupply = 4.82      # [V] DC supply voltage
print('Voltage supply, Vsupply =', Vsupply, '[V]')

# PWM steps used in the bench test (0..255), from the "Corrected Data"
# sheet of the Lab 9 spreadsheet.
PWM = np.array([255, 230, 205, 180, 155, 130, 105, 80, 55, 30, 5, 0])

# Motor-shaft speed [RPM] (column "w_m (RPM)" in the Corrected Data sheet;
# encoder reading on the motor shaft, before the gearbox).
wm_rpm = np.array([3639.97, 3249.97, 2840.0, 2450.0, 2029.98,
                   1649.99, 1250.0, 860.0, 470.0, 0.0, 0.0, 0.0])

# Output-shaft speed [RPM] (column "w_o(RPM)" in the Corrected Data sheet;
# equal to wm_rpm / GR within measurement noise).
wo_rpm = np.array([80.89, 72.44, 63.33, 54.22, 45.33,
                   36.67, 27.78, 19.11, 10.44, 0.0, 0.0, 0.0])

wm = 2 * np.pi * (wm_rpm / 60.0)   # motor speed   [rad/s]
wo = 2 * np.pi * (wo_rpm / 60.0)   # output speed  [rad/s]

# Motor input voltage at each PWM step
Vin = (PWM / 255.0) * Vsupply       # [V]

# Measured motor current [A], from DMM readings in the Corrected Data sheet.
# Sheet values are in mA, so divide by 1000 here.
Im = np.array([25.6, 24.3, 23.7, 23.0, 21.8,
               19.9, 17.0, 13.2,  8.9,  4.9, 0.8, 0.1]) / 1000.0

# Back-EMF at each PWM step (from electrical KVL across motor armature)
Vm = Vin - Rm * Im   # [V]


# ---- Linear Regression: rm = slope of Vm vs wm (rows where motor spins) ----
spin = wm > 0
xdata = wm[spin]
ydata = Vm[spin]

model = LinearRegression().fit(xdata.reshape(-1, 1), ydata)
Rsquared_rm = model.score(xdata.reshape(-1, 1), ydata)
slope_rm = model.coef_[0]
intercept_rm = model.intercept_

rm = slope_rm        # [V*s/rad] == [N*m/A]

print('Motor constant, rm =', rm, '[V*s/rad] (== N*m/A)')
print('Intercept          =', intercept_rm, '[V]')
print('R^2                =', Rsquared_rm)
print()


# ---- Plot 1: Vm vs wm ------------------------------------------------------
plt.figure(1, figsize=(6.0, 4.2))
plt.scatter(xdata, ydata, c='r', marker='x', s=60, label='Measured data')
xfit = np.linspace(0, xdata.max() * 1.05, 100)
plt.plot(xfit, slope_rm * xfit + intercept_rm,
         label=f'Linear fit: $V_m = {slope_rm:.4f}\\,\\omega_m + {intercept_rm:.3f}$\n$R^2 = {Rsquared_rm:.4f}$')
plt.xlabel(r'Motor speed $\omega_m$ [rad/s]')
plt.ylabel(r'Back-EMF $V_m$ [V]')
plt.title(r'Back-EMF vs Motor Speed')
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'vm_vs_wm.png'), dpi=200)


# %%--------------------------------------------------------------------------
# Step 3: Rotational damping Bm and Coulomb friction Tcf
print('Step 3: Finding rotational damping, Bm, and Coulomb friction, Tcf')

# Motor torque at each PWM step (gyrator law)
Tm = rm * Im   # [N*m]

# Linear regression on the spinning rows only
xdata = wm[spin]
ydata = Tm[spin]

model = LinearRegression().fit(xdata.reshape(-1, 1), ydata)
Rsquared_Bm = model.score(xdata.reshape(-1, 1), ydata)
slope_Bm = model.coef_[0]
intercept_Bm = model.intercept_

Bm  = slope_Bm        # [N*m*s/rad]
Tcf = intercept_Bm    # [N*m]  (== tau_mo, friction torque at omega_m = 0)

print('Rotational damping, Bm =', Bm, '[N*m*s/rad]')
print('Coulomb friction,  Tcf =', Tcf, '[N*m]')
print('R^2                    =', Rsquared_Bm)
print()


# ---- Plot 2: Tm vs wm ------------------------------------------------------
plt.figure(2, figsize=(6.0, 4.2))
plt.scatter(xdata, ydata, c='r', marker='x', s=60, label='Measured data')
xfit = np.linspace(0, xdata.max() * 1.05, 100)
plt.plot(xfit, slope_Bm * xfit + intercept_Bm,
         label=(f'Linear fit: $\\tau_m = {slope_Bm:.2e}\\,\\omega_m '
                f'+ {intercept_Bm:.2e}$\n$R^2 = {Rsquared_Bm:.4f}$'))
plt.xlabel(r'Motor speed $\omega_m$ [rad/s]')
plt.ylabel(r'Motor torque $\tau_m$ [N$\cdot$m]')
plt.title(r'Motor Torque vs Motor Speed (No-Load)')
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'tm_vs_wm.png'), dpi=200)


# %%--------------------------------------------------------------------------
# Step 4: Modeled output torque-speed curves
#
# At the gearbox output shaft, the torque-speed relation is:
#
#     T_o(omega_o) = GR * [ (rm/Rm)*Vin  -  GR*(rm^2/Rm + Bm)*omega_o ]
#
# Stall (omega_o = 0) torque:    T_stall = GR*(rm/Rm)*Vin
# No-load output speed:          omega_o_nl = (rm/Rm)*Vin / [GR*(rm^2/Rm + Bm)]
print('Step 4: Modeled torque-speed curves at output shaft')

V_list = [5.0, 4.5, 4.0, 3.5, 3.0]   # [V]
# Expanded form of T_o = GR*[(rm/Rm)*Vin - GR*(rm^2/Rm + Bm)*omega_o]:
#   T_o(omega_o) = GR*(rm/Rm)*Vin  -  GR^2 * (rm^2/Rm + Bm) * omega_o
slope_term = (GR ** 2) * (rm ** 2 / Rm + Bm)  # [N*m*s/rad] (Vin-independent)

# x-axis range: 0 -> a bit past the no-load output speed at the largest Vin
T_stall_max = GR * (rm / Rm) * max(V_list)
omega_o_nl_max = T_stall_max / slope_term
omega_o_axis = np.linspace(0, omega_o_nl_max * 1.02, 200)

plt.figure(3, figsize=(6.5, 4.6))
for V in V_list:
    T_stall = GR * (rm / Rm) * V
    T_o = T_stall - slope_term * omega_o_axis
    plt.plot(omega_o_axis, T_o, label=f'$V_{{in}} = {V:.1f}$ V')
    omega_o_nl_V = T_stall / slope_term
    print(f'  Vin = {V:.2f} V  ->  T_stall = {T_stall:.4e} N*m,  '
          f'omega_o_noload = {omega_o_nl_V:.3f} rad/s '
          f'({omega_o_nl_V*60/(2*np.pi):.1f} RPM)')

plt.axhline(0, color='k', lw=0.6)
plt.xlabel(r'Output shaft speed $\omega_o$ [rad/s]')
plt.ylabel(r'Output torque $\tau_o$ [N$\cdot$m]')
plt.title(r'Modeled Output Torque-Speed Curves')
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'torque_speed_family.png'), dpi=200)


# %%--------------------------------------------------------------------------
# Summary
print()
print('==================== SUMMARY (SI units) ====================')
print(f' Rm  = {Rm:.3f}     [Ohm]')
print(f' rm  = {rm:.6f}  [V*s/rad]   (R^2 = {Rsquared_rm:.4f})')
print(f' Bm  = {Bm:.6e} [N*m*s/rad] (R^2 = {Rsquared_Bm:.4f})')
print(f' Tcf = {Tcf:.6e} [N*m]')
print(f' GR  = {GR}')
print('============================================================')

# plt.show()  # disabled for headless runs
