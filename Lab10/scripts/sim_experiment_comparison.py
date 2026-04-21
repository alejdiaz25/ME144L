"""
Lab 10 prelab: sim vs experiment comparison (open-loop PMDC).

For three desired speeds pulled from the Lab 9 steady-state test (taken
at different rotational speeds), this script:

  1. Computes the open-loop PWM command predicted by the torque-speed
     model, using the motor parameters extracted in Lab 9.
  2. Integrates the PMDC ODE with that constant command to get the
     simulated steady-state motor speed.
  3. Compares both PWM_sim and omega_ss_sim against the measured
     experimental values.
  4. Prints a summary table and saves a comparison figure to ../figures/.

Parameters and the ODE are consistent with pmdc_motor_OL_sim.py.
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt


# -----------------------------------------------------------------
# Motor parameters from Lab 9 steady-state testing (SI units)
# -----------------------------------------------------------------
rm    = 1.011e-2
Rm    = 26.9
Bm    = 4.71e-7
taumo = 9.81e-5
GR    = 45
Jm    = 0.5 * 0.009 * (0.25/39.37)**2
Vb    = 4.82


# -----------------------------------------------------------------
# Three operating points from the Lab 9 "Corrected Data" sheet.
# omega_m [rad/s] is converted from the measured motor-shaft RPM.
# -----------------------------------------------------------------
exp_points = [
    # (label,     PWM_exp, wm_rpm_exp)
    ("high",      230,     3249.97),
    ("mid",       155,     2029.98),
    ("low",        80,      860.00),
]


def pmdc(x, t, rm, Rm, Bm, Jm, tauo, Vin):
    omegam, thetam = x[0], x[1]
    im = (Vin - rm*omegam) / Rm
    omegamdot = (rm*im - Bm*omegam - tauo*np.tanh(omegam/60)) / Jm
    thetamdot = omegam
    return np.array([omegamdot, thetamdot]), im


def rk4fixed(f, x0, t, args=()):
    n = len(t)
    x = np.zeros((n, len(x0)))
    x[0] = x0
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1, _ = f(x[i],              t[i],         *args)
        k2, _ = f(x[i] + k1*h/2.0,   t[i] + h/2.0, *args)
        k3, _ = f(x[i] + k2*h/2.0,   t[i] + h/2.0, *args)
        k4, _ = f(x[i] + k3*h,       t[i] + h,     *args)
        x[i+1] = x[i] + (h/6.0) * (k1 + 2*k2 + 2*k3 + k4)
    return x


def simulate_to_steady_state(omega_d):
    """Apply the open-loop command for omega_d and return (PWM_sim,
    Vin_sim, omega_ss_sim) after the motor has settled."""
    mcc     = (Rm*(taumo*np.tanh(omega_d) + Bm*omega_d)/rm + rm*omega_d) / Vb
    PWM_sim = mcc * 255
    Vin_sim = mcc * Vb

    # Integrate long enough to settle (rotor time constant is ms-scale)
    t  = np.linspace(0, 1.0, 2001)
    x0 = np.array([0.0, 0.0])
    sol = rk4fixed(pmdc, x0, t, args=(rm, Rm, Bm, Jm, taumo, Vin_sim))
    omega_ss = float(np.mean(sol[-200:, 0]))      # avg last 100 ms
    return PWM_sim, Vin_sim, omega_ss


def main():
    rows = []
    for label, PWM_exp, wm_rpm_exp in exp_points:
        omega_d_exp = 2*math.pi*wm_rpm_exp/60.0
        PWM_sim, Vin_sim, omega_ss = simulate_to_steady_state(omega_d_exp)
        pct_pwm   = 100.0 * (PWM_sim  - PWM_exp)     / PWM_exp
        pct_omega = 100.0 * (omega_ss - omega_d_exp) / omega_d_exp
        rows.append({
            "label":      label,
            "PWM_exp":    PWM_exp,
            "wm_exp":     omega_d_exp,
            "rpm_exp":    wm_rpm_exp,
            "PWM_sim":    PWM_sim,
            "Vin_sim":    Vin_sim,
            "omega_ss":   omega_ss,
            "pct_pwm":    pct_pwm,
            "pct_omega":  pct_omega,
        })

    # ---------------- printed summary table ----------------
    print()
    print("=" * 86)
    print(" Open-loop PMDC: simulation vs Lab 9 experimental steady-state points")
    print("=" * 86)
    hdr = (" {lbl:>5} | {pe:>7} | {we:>9} | {ps:>8} | {vs:>7} | "
           "{ws:>9} | {dp:>7} | {dw:>7}")
    print(hdr.format(lbl="case",  pe="PWM_exp", we="w_exp",
                     ps="PWM_sim", vs="Vin_sim", ws="w_ss_sim",
                     dp="dPWM %", dw="dw %"))
    print(hdr.format(lbl="",      pe="[int]",   we="[rad/s]",
                     ps="[int]",   vs="[V]",     ws="[rad/s]",
                     dp="",        dw=""))
    print("-" * 86)
    for r in rows:
        print(" {lbl:>5} | {pe:>7d} | {we:>9.2f} | {ps:>8.2f} | "
              "{vs:>7.3f} | {ws:>9.2f} | {dp:>6.2f}% | "
              "{dw:>6.2f}%".format(
                  lbl=r["label"],
                  pe=r["PWM_exp"],   we=r["wm_exp"],
                  ps=r["PWM_sim"],   vs=r["Vin_sim"],
                  ws=r["omega_ss"],  dp=r["pct_pwm"],
                  dw=r["pct_omega"]))
    print("=" * 86)
    print()

    # ---------------- comparison figure ----------------
    fig_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "figures"))
    os.makedirs(fig_dir, exist_ok=True)

    labels    = [f"{r['rpm_exp']:.0f} RPM" for r in rows]
    PWM_sims  = [r["PWM_sim"] for r in rows]
    PWM_exps  = [r["PWM_exp"] for r in rows]

    x = np.arange(len(rows))
    w = 0.35

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.bar(x - w/2, PWM_exps, w, label="Experimental PWM", color="#c0392b")
    ax.bar(x + w/2, PWM_sims, w, label="Simulated PWM",    color="#2980b9")
    for xi, ps, pe in zip(x, PWM_sims, PWM_exps):
        pct = 100.0*(ps - pe)/pe
        ax.annotate(f"{pct:+.1f}%",
                    xy=(xi + w/2, ps),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("PWM [int]")
    ax.set_title("Open-loop PWM: torque-speed model vs Lab 9 experiment")
    ax.legend(loc="upper left")
    ax.grid(True, axis="y", alpha=0.4)
    fig.tight_layout()
    out_path = os.path.join(fig_dir, "sim_vs_exp_pwm.png")
    fig.savefig(out_path, dpi=200)
    print(f"Saved comparison figure -> {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
