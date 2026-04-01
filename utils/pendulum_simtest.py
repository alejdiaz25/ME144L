#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 23:20:35 2026

@author: alejandrodiaz
"""

# DSCLab 
# Compound pendulum simulation (Updated for Pendulum #3)

import numpy as np
import matplotlib.pyplot as plt

def main():
	# System parameter list (Updated with values from ME 144L Pre Lab 4)
	m = 0.1572          # Total Mass (kg) 
	g = 9.81
	l = 0.19285         # Distance from Pivot to CG (L_cm) [cite: 95]
	I = 6.479e-3        # Moment of Inertia about pivot (kg-m^2) 

	# initially deflect and release mass from rest
	x0 = np.array([np.pi/2, 0.0])
	t = np.linspace(0, 4, 501)
	
	# Added 'I' to the arguments passed to the solver
	sol = rk4fixed(pendulum, x0, t, args=(m,g,l,I))
	
	tau_theta = np.zeros(len(t))
	for i in range(len(t)):
		# Added 'I' to the function call
		_, y = pendulum(sol[i,:],t[i],m,g,l,I)
		tau_theta[i] = y

	# plot results
	plt.rcParams["figure.figsize"] = [7,5]
	plt.rcParams["figure.autolayout"] = True
	fig, (ax1,ax2,ax3) = plt.subplots(3)
	ax1.plot(t, sol[:,0]*180/np.pi, 'k')
	ax1.set_ylabel(r'$\theta$, deg')
	ax2.plot(t, sol[:,1], 'k')
	ax2.set_ylabel(r'$\omega$, rad/sec')
	ax3.plot(t, tau_theta, 'k')
	ax3.set_ylabel(r'$\tau_{\theta}$, Nm')
	plt.xlabel('Time (sec)')
	# plt.savefig("pendulum_sim_results_1.svg")
	plt.show()

# define the system ODEs
def pendulum(x, t, m, g, l, I): # Added 'I' argument
	theta, omega = x[0], x[1]
	tau_theta = m*g*l*np.sin(theta)
	theta_dot = omega
	
	# UPDATED: Use I instead of (m*l**2) for compound pendulum dynamics
	omega_dot = -tau_theta/I
	
	# specify outputs
	y = tau_theta

	return np.array([theta_dot, omega_dot]), y

# This is a fixed-step, 4th order Runge-Kutta
# Never have to change this routine
def rk4fixed(f, x0, t, args=()):
    import numpy
    n = len(t)
    x = numpy.zeros((n, len(x0)))
    x[0] = x0
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1, _ = f(x[i], t[i], *args)
        k2, _ = f(x[i] + k1 * h / 2., t[i] + h / 2., *args)
        k3, _ = f(x[i] + k2 * h / 2., t[i] + h / 2., *args)
        k4, _ = f(x[i] + k3 * h, t[i] + h, *args)
        x[i+1] = x[i] + (h / 6.) * (k1 + 2*k2 + 2*k3 + k4)
    return x

def rk1fixed(f, x0, t, args=()):
    import numpy
    N = len(t)
    x = numpy.zeros((N, len(x0)))
    x[0] = x0
    for i in range(N - 1):
        k1, _ = f(x[i], t[i], *args)
        x[i+1] = x[i] + (t[i+1] - t[i]) * k1
    return x

main()