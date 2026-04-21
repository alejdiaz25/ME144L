"""
generate_report_figures.py
Generates simulation-based figures for the Lab 10 report.
Produces:
  1. ol_sim_vs_exp.png  – OL sim steady-state vs experimental (3 setpoints)
  2. cl_sim_step.png    – CL PID+FF simulation step response (sim vs exp comparison)
"""
import os
import math
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

# ─────────────────────────────────────────────
# Motor parameters (Lab 9 values, SI)
# ─────────────────────────────────────────────
rm    = 1.011e-2   # V·s/rad  (motor constant)
Rm    = 26.9       # Ω        (armature resistance)
Bm    = 4.71e-7    # N·m·s/rad (viscous damping)
taumo = 9.81e-5    # N·m       (Coulomb friction)
GR    = 45         # gearbox reduction
Vb    = 4.82       # V         (bus voltage)
Jm    = 1.45e-7    # kg·m²     (rotor inertia)

# OL gain (from Lab 10 regression, through origin)
OL_gain       = 0.7457   # PWM / (rad/s)  – original regression
OL_gain_tuned = 0.70     # tuned for CL

# Experimental OL data (from xlsx serial monitor)
wm_refs = np.array([250.0, 300.0, 350.0])
wm_exps = np.array([261.80, 303.69, 366.49])
pwm_exps = np.array([186, 224, 255])

# Added inertia disk (on OUTPUT shaft)
m_disk       = 0.39       # kg
r_disk       = 0.1015     # m
J_disk       = 0.5 * m_disk * r_disk**2          # 2.009e-3 kg·m²
J_reflected  = J_disk / GR**2                    # 9.92e-7  kg·m²
Jm_loaded    = Jm + J_reflected                  # 1.137e-6 kg·m²

# CL gains (final values from xlsx)
Kp = 0.05; Ki = 0.10; Kd = 0.0

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({'font.size': 10, 'figure.dpi': 150})

# ─────────────────────────────────────────────
# PMDC ODE (inductance neglected)
# ─────────────────────────────────────────────
def pmdc(x, _t, Vin):
    wm = x[0]
    im = (Vin - rm * wm) / Rm
    wmdot = (rm * im - Bm * wm - taumo * np.tanh(wm / 60.0)) / Jm
    return np.array([wmdot, wm])

def pmdc_loaded(x, _t, Vin):
    wm = x[0]
    im = (Vin - rm * wm) / Rm
    wmdot = (rm * im - Bm * wm - taumo * np.tanh(wm / 60.0)) / Jm_loaded
    return np.array([wmdot, wm])

def rk4fixed(f, x0, t, args=()):
    n = len(t)
    x = np.zeros((n, 2))
    x[0] = x0
    for i in range(n - 1):
        h = t[i + 1] - t[i]
        k1 = f(x[i],           t[i],       *args)
        k2 = f(x[i] + k1*h/2,  t[i]+h/2,   *args)
        k3 = f(x[i] + k2*h/2,  t[i]+h/2,   *args)
        k4 = f(x[i] + k3*h,    t[i]+h,     *args)
        x[i + 1] = x[i] + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)
    return x

def simulate_step(wm_ref, gain, Jm_eff=None, t_step=1.0, t_total=8.0, dt=0.01):
    """Simulate OL step from 0 to wm_ref then back to 0."""
    if Jm_eff is None:
        Jm_eff = Jm

    pwm_cmd = float(np.clip(gain * wm_ref, 0, 255))
    Vin = pwm_cmd / 255 * Vb

    ts = np.arange(0, t_total + dt, dt)
    wm_arr = []
    x = np.array([0.0, 0.0])

    for i in range(len(ts) - 1):
        t_on  = t_step
        t_off = t_total - t_step
        V = Vin if (ts[i] >= t_on and ts[i] < t_off) else 0.0
        tc = np.linspace(ts[i], ts[i + 1], 21)
        sol = rk4fixed(pmdc if Jm_eff == Jm else pmdc_loaded,
                       x, tc, args=(V,))
        x = sol[-1]
        wm_arr.append(x[0])

    return ts[:-1], np.array(wm_arr)

def steady_state_speed(Vin_val):
    """Integrate ODE to steady state and return final speed."""
    ts = np.arange(0, 6.0, 0.005)
    x = np.array([0.0, 0.0])
    for i in range(len(ts) - 1):
        tc = np.linspace(ts[i], ts[i + 1], 11)
        sol = rk4fixed(pmdc, x, tc, args=(Vin_val,))
        x = sol[-1]
    return x[0]


# ═══════════════════════════════════════════════════════════════
# Figure 1 – OL Simulation vs Experiment (steady-state comparison)
# ═══════════════════════════════════════════════════════════════
print("Computing OL steady-state predictions …")
wm_sims = []
for wref in wm_refs:
    pwm_cmd = float(np.clip(OL_gain * wref, 0, 255))
    Vin = pwm_cmd / 255 * Vb
    wm_ss = steady_state_speed(Vin)
    wm_sims.append(wm_ss)
wm_sims = np.array(wm_sims)

x_pos = np.arange(len(wm_refs))
bar_w = 0.28
colors = {'ref': '#95a5a6', 'sim': '#2980b9', 'exp': '#c0392b'}

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.bar(x_pos - bar_w, wm_refs,  bar_w, label='Setpoint $\\omega_{ref}$',
       color=colors['ref'], edgecolor='k', linewidth=0.6)
ax.bar(x_pos,          wm_sims, bar_w, label='ODE Simulation $\\omega_{ss}$',
       color=colors['sim'], edgecolor='k', linewidth=0.6)
ax.bar(x_pos + bar_w,  wm_exps, bar_w, label='Experiment $\\omega_{exp}$',
       color=colors['exp'], edgecolor='k', linewidth=0.6)

# Annotate percent errors
for i, (ws, we) in enumerate(zip(wm_sims, wm_exps)):
    err_pct = 100*(ws - we)/we
    ax.text(x_pos[i], max(ws, we) + 6, f'{err_pct:+.1f}%',
            ha='center', va='bottom', fontsize=8, color='#555')

ax.set_xticks(x_pos)
ax.set_xticklabels([f'$\\omega_{{ref}}$ = {int(w)} rad/s' for w in wm_refs])
ax.set_ylabel('Motor shaft speed [rad/s]')
ax.set_title('Open-Loop Control: ODE Simulation vs Experiment (3 setpoints)')
ax.legend(fontsize=9)
ax.set_ylim(0, 420)
ax.grid(True, axis='y', alpha=0.4)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'ol_sim_vs_exp.png'), dpi=200)
plt.close(fig)

for i in range(3):
    print(f"  wm_ref={wm_refs[i]:.0f}  sim={wm_sims[i]:.1f}  exp={wm_exps[i]:.2f}  "
          f"err={100*(wm_sims[i]-wm_exps[i])/wm_exps[i]:+.1f}%")
print("[Fig 1] ol_sim_vs_exp.png saved")


# ═══════════════════════════════════════════════════════════════
# Figure 2 – CL PID+FF simulation step response
# Reference schedule: 0 → 300 → 200 → 300 → 200 → 0 rad/s
# Matches experimental pattern in images 10 and 12
# ═══════════════════════════════════════════════════════════════
dt_ctrl = 0.05          # 20 Hz controller (50 ms loop time)
t_total_cl = 30.0

def ref_schedule(t):
    """Return desired speed at time t to match experimental pattern."""
    if   5.5 <= t < 11.0: return 300.0
    elif 11.0 <= t < 16.0: return 200.0
    elif 19.0 <= t < 24.5: return 300.0
    elif 24.5 <= t < 29.0: return 200.0
    return 0.0

ts_cl = np.arange(0, t_total_cl + dt_ctrl, dt_ctrl)
wm_arr_cl   = [0.0]
pwm_arr_cl  = [0]
ref_arr_cl  = [0.0]
err_arr_cl  = [0.0]

x = np.array([0.0, 0.0])
sum_e = 0.0
e_last = 0.0

for i in range(len(ts_cl) - 1):
    wm_ref_i = ref_schedule(ts_cl[i])
    e = wm_ref_i - x[0]
    sum_e += e * dt_ctrl
    dedt = (e - e_last) / dt_ctrl
    # Anti-windup: clamp integral contribution
    sum_e = float(np.clip(sum_e, -255/Ki, 255/Ki)) if Ki > 0 else sum_e

    ff   = OL_gain_tuned * wm_ref_i
    u    = ff + Kp * e + Ki * sum_e + Kd * dedt
    pwm  = int(np.clip(round(u), 0, 255))
    Vin  = pwm / 255 * Vb

    tc  = np.linspace(ts_cl[i], ts_cl[i + 1], 21)
    sol = rk4fixed(pmdc, x, tc, args=(Vin,))
    x   = sol[-1]
    # Add encoder noise (Arduino reads speed every ~50 ms)
    wm_noisy = x[0] + rng.normal(0, 5.0)

    wm_arr_cl.append(wm_noisy)
    pwm_arr_cl.append(pwm)
    ref_arr_cl.append(wm_ref_i)
    err_arr_cl.append(e)
    e_last = e

wm_arr_cl  = np.array(wm_arr_cl)
pwm_arr_cl = np.array(pwm_arr_cl)
ref_arr_cl = np.array(ref_arr_cl)
err_arr_cl = np.array(err_arr_cl)

fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7.0, 5.5), sharex=True)

ax_top.plot(ts_cl, ref_arr_cl, 'b-',  lw=1.8, label=r'$\omega_{m,\mathrm{ref}}$ [rad/s]')
ax_top.plot(ts_cl, wm_arr_cl,  color='orange', lw=1.1, label=r'$\omega_m$ (sim) [rad/s]')
ax_top.step(ts_cl, pwm_arr_cl, where='post', color='green', lw=1.0,
            label='PWM [Int]', alpha=0.8)
ax_top.set_ylabel('Amplitude')
ax_top.set_title(
    f'CL Simulation: PID+FF  ($K_p={Kp}$, $K_i={Ki}$, $K_d={Kd}$,  FF={OL_gain_tuned})',
    fontsize=10)
ax_top.legend(fontsize=8, loc='upper right')
ax_top.grid(True, alpha=0.35)
ax_top.set_ylim(-10, 320)

ax_bot.plot(ts_cl, err_arr_cl, color='#2980b9', lw=1.1,
            label=r'$\omega_m$ error [rad/s]')
ax_bot.step(ts_cl, pwm_arr_cl, where='post', color='orange', lw=1.0,
            label='PWM [int]', alpha=0.8)
ax_bot.axhline(0, color='k', lw=0.7, ls=':')
ax_bot.set_ylabel('Amplitude')
ax_bot.set_xlabel('Time [s]')
ax_bot.legend(fontsize=8, loc='upper right')
ax_bot.grid(True, alpha=0.35)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'cl_sim_step.png'), dpi=200)
plt.close(fig)

# Steady-state error at each speed
ss_300 = np.mean(wm_arr_cl[(ts_cl >= 8) & (ts_cl < 11)])
ss_200 = np.mean(wm_arr_cl[(ts_cl >= 13) & (ts_cl < 16)])
print(f"[Fig 2] cl_sim_step.png saved  "
      f"ss@300={ss_300:.1f} rad/s  ss@200={ss_200:.1f} rad/s")

print("\nAll figures saved to:", OUT_DIR)
print(f"\nDisk inertia summary:")
print(f"  J_disk      = {J_disk:.4e} kg·m²  (on output shaft)")
print(f"  J_reflected = {J_reflected:.4e} kg·m²  (reflected to motor shaft, GR={GR})")
print(f"  Jm_loaded   = {Jm_loaded:.4e} kg·m²  = {Jm_loaded/Jm:.1f}× original")
