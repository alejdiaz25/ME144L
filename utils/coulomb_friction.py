import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# PART 2: SIMULATION vs MEASURED PLOT
# ============================================================

# --- Calibration ---
K      = 45.26882157895809
theta0 = -108.52517178949941 - 8.72

# --- Load measured data ---
# Ensure 'test1771356862.csv' is in the same directory as this script
data = pd.read_csv('test1771356862.csv')
time_meas    = np.array(data['Time'])
voltage_meas = np.array(data['voltage'])
theta_meas   = K * voltage_meas + theta0

# --- Compound pendulum ODE ---
def comp_pendulum(x, t, m, g, Jo, Lc, tauo, b):
    theta, omega = x
    theta_dot = omega
    tau_theta = -b * omega - tauo * np.sign(omega) - m * g * Lc * np.sin(theta)
    omega_dot = tau_theta / Jo
    return np.array([theta_dot, omega_dot]), tau_theta

# --- RK4 integrator ---
def rk4fixed(f, x0, t, args=()):
    n = len(t)
    x = np.zeros((n, len(x0)))
    x[0] = x0
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1, _ = f(x[i],              t[i],       *args)
        k2, _ = f(x[i] + k1*h/2,     t[i]+h/2,   *args)
        k3, _ = f(x[i] + k2*h/2,     t[i]+h/2,   *args)
        k4, _ = f(x[i] + k3*h,       t[i]+h,     *args)
        x[i+1] = x[i] + (h/6.)*(k1 + 2*k2 + 2*k3 + k4)
    return x

# --- Pendulum 3 parameters (from sim file) ---
m    = 0.1574
g    = 9.81
Lc   = 0.1992
Jo   = 0.4 * 0.017
b    = 0.0025 * 0.00175 * 3
tauo = 0.15 * 0.0125 * 2.65
args = (m, g, Jo, Lc, tauo, b)

print(f"m    = {m} kg")
print(f"Lc   = {Lc} m")
print(f"Jo   = {Jo:.5f} kg·m²")
print(f"b    = {b:.8f} N·m·s/rad")
print(f"tauo = {tauo:.6f} N·m")

init_angle = np.pi / -2
init_time  = 3
x0 = np.array([init_angle, 0.0])
t  = np.linspace(init_time, 30, 501)

sol = rk4fixed(comp_pendulum, x0, t, args=args)

# --- Compute friction torques ---
tau_total   = np.zeros(len(t))
tau_viscous = np.zeros(len(t))
tau_coulomb = np.zeros(len(t))

for i in range(len(t)):
    theta_i, omega_i = sol[i, :]
    tau_viscous[i]  = -b * omega_i
    tau_coulomb[i]  = -tauo * np.sign(omega_i)
    tau_total[i]    = tau_viscous[i] + tau_coulomb[i]  # friction only (no gravity)

# --- PLOT 2: Simulated vs Measured ---
theta_deg = sol[:, 0] * 180 / np.pi

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(t, theta_deg, 'k-', linewidth=1.8, label='Simulated $\\theta(t)$')
ax.plot(time_meas, theta_meas, color='crimson', linewidth=1.2, alpha=0.85, label='Measured $\\theta(t)$')
ax.set_xlabel('Time (s)')
ax.set_ylabel(r'$\theta$ (deg)')
ax.set_title('Simulated vs. Measured Pendulum Angle — Pendulum 3')
ax.legend()
ax.grid(True, alpha=0.35)
plt.tight_layout()

# Save locally to the current folder, then display
plt.savefig('sim_vs_meas.png', dpi=180, bbox_inches='tight')
plt.show() 
print("Sim vs measured plot saved and displayed.")

# --- PLOT 3: Friction torque decomposition ---
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(t, tau_total,   'k-',  linewidth=1.8, label=r'Total Friction Torque $\tau_{friction}$')
ax.plot(t, tau_viscous, 'b--', linewidth=1.5, label=r'Viscous Damping $\tau_b = -b\omega$')
ax.plot(t, tau_coulomb, 'r:', linewidth=1.8, label=r'Coulomb Friction $\tau_0 = -\tau_0 \cdot \mathrm{sign}(\omega)$')
ax.axhline(0, color='gray', linewidth=0.8, linestyle='-')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Torque (N·m)')
ax.set_title('Friction Torque Components Over Time — Pendulum 3')
ax.legend()
ax.grid(True, alpha=0.35)
plt.tight_layout()

# Save locally to the current folder, then display
plt.savefig('friction_torques.png', dpi=180, bbox_inches='tight')
plt.show() 
print("Friction torque plot saved and displayed.")

# Print magnitudes for analysis
print(f"\nMean |tau_viscous| = {np.mean(np.abs(tau_viscous)):.6f} N·m")
print(f"Mean |tau_coulomb| = {np.mean(np.abs(tau_coulomb)):.6f} N·m")
print(f"Max  |tau_viscous| = {np.max(np.abs(tau_viscous)):.6f} N·m")
print(f"Max  |tau_coulomb| = {np.max(np.abs(tau_coulomb)):.6f} N·m")