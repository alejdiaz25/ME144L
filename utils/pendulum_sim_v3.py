#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 13:38:25 2026

@author: alejandrodiaz
"""

# DSCLab: pendulum_sim_v3.py
# Pendulum Simulation for PL3 Q4

"""
From: GN
Date: Summer 25
Comment: 
    I modified Prof. Longoria's pendulum_sim.py code from PL3 so that it can accommodate
    both simple and compound pendulum for PL3 Q4. I also added blocks of code to plot 
    the measured values from the lab experiment.
   

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def main():
    
# ===================================================================================
# ================ Set Up for Measured Values from Physical Pendulum ================

    # --- Read the file ---
    data = pd.read_csv("/Users/alejandrodiaz/Downloads/test1771356862.csv")     # NOTE: Replace with your actual filename


    time_meas = np.array(data["Time"])
    voltage_meas = np.array(data["voltage"])
    

    # --- Write down calibration values ---
    K = 45.26882157895809           # NOTE: Replace with calibration value
    theta0 = -108.52517178949941 - 8.72    # NOTE: Replace with calibration value
    theta_meas = K * voltage_meas + theta0
    

# ===================================================================================
# ======================== Set Up for Simulation of Pendulum  =======================


    # NOTE: Toggle between Simple and Compound Pendulum by commenting/uncommenting 

    # --- Simple Pendulum Parameters ---
    # m = 1
    # g = 9.81
    # l = g / (4 * np.pi**2)  # Prof designed l so that T = 2π√(l/g) = 1s → solve for l ⇒ l = g / (4π²)
    # pend_fn = pendulum
    # args = (m, g, l)

  
    # --- Compound Pendulum (PL3) Parameters ---
    # NOTE: Replace the m, Lc, Jo values below
    # NOTE: Keep b, tau0 as is -- tune later
    m = 0.1574                    # kg
    g = 9.81                     # m/s²
    Lc = 0.1992                  # Center of gravity location from pivot (m)
    Jo = 0.006479 * 1.1          # Moment of inertia about pivot (kg·m²)
    b = 0.0025*0.00175 * 1                  # Viscous damping coefficient (N·m·s/rad)
    tauo = 0.15*0.0125 * 2.7                # Coulomb friction torque (N·m)
    pend_fn = comp_pendulum
    args = (m, g, Jo, Lc, tauo, b)

    
    # --- Simulation setup ---
    init_angle = np.pi/-2 # initial angle (-90°);   NOTE: You can change this if you didnt start at -90deg
    init_time = 3 # initial time;                 NOTE: You can change this if you didnt start at t=0

    x0 = np.array([init_angle, 0.0])  # initial angle, zero velocity
    t = np.linspace(init_time, 30, 501) # NOTE: Change the second value to the same recordtime 
    sol = rk4fixed(pend_fn, x0, t, args=args)
    tau_theta = np.zeros(len(t))

    for i in range(len(t)):
        _, y = pend_fn(sol[i, :], t[i], *args)
        tau_theta[i] = y
        
        
        
# ===================================================================================
# ===== Set Up for Plotting both Simulation and Measured Behaviors of Pendulum  =====


    # NOTE: There are two plotters below, PLOT 1 shows full plot and PLOT 2 shows first "t_limit" seconds
    #       You can use PLOT 2 to zoom in on your plot if necessary

    # --- PLOT 1: Plotting Simulated and Measured Values ---
    plt.rcParams["figure.figsize"] = [7, 5]
    plt.rcParams["figure.autolayout"] = True
    fig, (ax1) = plt.subplots(1)
    theta_deg = sol[:, 0] * 180 / np.pi
    ax1.plot(t, theta_deg, 'k', label='Simulated θ(t)')
    ax1.plot(time_meas, theta_meas, color='red', label='Measured θ(t)')
    #ax1.scatter(time_meas, theta_meas, color='red', s=2, label='Measured θ(t)') # scatter plot for measured value
    
    ax1.set_ylabel(r'$\theta$, deg')
    ax1.set_xlabel('Time (sec)')
    ax1.set_title("Simulated vs Measured Pendulum Angle")
    ax1.legend()
    ax1.grid(True)
    plt.savefig("pendulum_sim_vs_meas.svg")
    plt.show()
    
    
    
    #  --- PLOT 2: Plot first :t_limit" seconds of Simulated and Measured Values ---
    # NOTE: Make sure you comment out PlOT 1 code block above to use PLOT 2
    
    # t_limit = 20  # time limit for plot;        NOTE: Change if necessary

    # theta_deg = sol[:, 0] * 180 / np.pi

    # mask_sim = t <= t_limit
    # t_plot = t[mask_sim]
    # theta_plot = theta_deg[mask_sim]   
    
    
    # mask_meas = time_meas <= t_limit
    # time_meas_plot = time_meas[mask_meas]
    # theta_meas_plot = theta_meas[mask_meas]
    
    # plt.figure(figsize=(7, 4))
    # plt.plot(t_plot, theta_plot, 'k-', label='Simulated θ(t)')
    # plt.plot(time_meas_plot, theta_meas_plot, 'r--', label='Measured θ(t)')
    # plt.xlabel("Time (sec)")
    # plt.ylabel(r"$\theta$ (deg)")
    # plt.title("Pendulum Angle vs Time (First 10s)")
    # plt.legend(loc='upper right')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
    



# --- Simple pendulum ODE ---
def pendulum(x, t, m, g, l):
    theta, omega = x
    tau_theta = m * g * l * np.sin(theta)
    theta_dot = omega
    omega_dot = -tau_theta / (m * l**2)
    # Simple pendulum dynamics:
    #   τ = m·g·l·sin(θ)
    #   ω̇ = τ / (m·l²) = g·sin(θ) / l
    
    return np.array([theta_dot, omega_dot]), tau_theta


# --- Compound pendulum ODE (PL3) ---
def comp_pendulum(x, t, m, g, Jo, Lc, tauo, b):
    theta, omega = x
    theta_dot = omega
    tau_theta = -b * omega - tauo * np.sign(omega) - m * g * Lc * np.sin(theta)
    omega_dot = tau_theta / Jo
    # Compound pendulum dynamics:
    # ω̇ = (τ_net) / Jo, where:
    #   - τ_net = -b·ω              (viscous damping)
    #             - τ₀·sign(ω)      (Coulomb friction)
    #             - m·g·Lc·sin(θ)   (gravity)

    return np.array([theta_dot, omega_dot]), tau_theta

    

# --- RK4 fixed-step integrator ---
def rk4fixed(f, x0, t, args=()):
    n = len(t)
    x = np.zeros((n, len(x0)))
    x[0] = x0
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1, _ = f(x[i], t[i], *args)
        k2, _ = f(x[i] + k1 * h / 2., t[i] + h / 2., *args)
        k3, _ = f(x[i] + k2 * h / 2., t[i] + h / 2., *args)
        k4, _ = f(x[i] + k3 * h, t[i] + h, *args)
        x[i+1] = x[i] + (h / 6.) * (k1 + 2*k2 + 2*k3 + k4)
    return x


# --- RK1 (Euler) fixed-step integrator ---
def rk1fixed(f, x0, t, args=()):
    n = len(t)
    x = np.zeros((n, len(x0)))
    x[0] = x0
    for i in range(n - 1):
        k1, _ = f(x[i], t[i], *args)
        x[i+1] = x[i] + (t[i+1] - t[i]) * k1
    return x


main()
