#
# Pendulum simulation
#
import numpy as np
import math
import matplotlib.pyplot as plt

def main():
    # define system parameters
    g = 9.81 # gravitational accel, m/s^2
    m = 0.172 # total mass, kg
    L = 0.1467 # total length of phone, m
    Lc = L/2 # CG location, m
    Jo = m*Lc*(2*Lc) # mass moment of inertial, kg*m^2
    # set initial state conditions
    # initially deflect and release mass from rest
    # x = [angle, omega]
    x0 = np.array([0.035, 0.0])
    # define the time array
    t = np.linspace(0,0.65, 1001)
    sol = rk4fixed(comp_invpendulum, x0, t, args=(m, g, Jo, Lc))
    
    # --- NEW CODE Start ---
    # 1. Define the impact condition (90 degrees in radians)
    impact_angle = np.pi / 2 

    # 2. Find indices where the angle is greater than or equal to 90 degrees
    # sol[:, 0] contains the angles (theta)
    impact_indices = np.where(sol[:, 0] >= impact_angle)[0]

    if len(impact_indices) > 0:
        # Get the first index where impact occurs
        idx = impact_indices[0]
        
        # Extract time and angular velocity at that index
        time_of_impact = t[idx]
        max_omega = sol[idx, 1] # sol[:, 1] contains omega
        
        print(f"Impact detected at step index: {idx}")
        print(f"Time of impact: {time_of_impact:.4f} s")
        print(f"Angular velocity at impact: {max_omega:.4f} rad/s")
        
        # Optional: Add a red dot to the plot to mark impact
        plt.scatter([time_of_impact], [max_omega], color='red', zorder=5, label='Impact')
        
    else:
        print("The pendulum did not reach 90 degrees within the simulation time.")
        
    # --- NEW CODE END ---
    
    # ok, it ran ok, working...
    print('Plotting...')

    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    fig, (ax1, ax2) = plt.subplots(2)
    ax1.plot(t, sol[:,0]*180/math.pi, 'k', label='theta')
    ax1.legend(loc="upper right")
    ax2.plot(t, sol[:,1], 'k', label='omega')
    ax2.legend(loc="upper right")
    plt.xlabel('Time (sec)')
    plt.tight_layout()
    plt.show()
    # sometimes I like to save to *.svg
    #plt.savefig("Raw_data_1_plots.svg")
    
# Define some of the subroutines

# define the system ODEs
def comp_invpendulum(x, t, m, g, Jo, Lc):
	xdot1 = x[1]
	xdot2 = + m*g*Lc*np.sin(x[0])/Jo
	# specify outputs
	y = 0

	return np.array([xdot1, xdot2]), y

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

main()
