#
# Flywheel decay with tachometer sensor simulation
# Plots flywheel angular position and speed and tachometer simulated output
# Results saved to csv file on line 69
#
import numpy as np
from scipy import signal
import pandas as pd
import math
import matplotlib.pyplot as plt

def main():
    # define system parameters
    # Flywheel rotational inertia, assume steel, 6 inch radius
    rho = 7850 # kg/m^3
    R = 6/39.37 # radius, m
    A = np.pi*R**2 # area
    w = 6/39.37 # disk thickness, m
    m = rho*A*w # total mass
    J = 0.5*m*R*R # mass moment of inertial, kg*m^2
    print(f"J = {J:.4f} kg*m^2")
    B = 10 # linear friction coefficient
    print(f"Time constant, tau = J/B = {J/B:.4f} sec")

    # Tachometer sensor model - converts omega (rad/sec) to voltage signal with noise
    # This model is implemented as an output signal in the simulation; see ODEs function
    Ktach = 0.1     # Calibration: volts/(rad/sec)
    # Noise model parameters used in np.random.normal() (assume Gaussian noise)
    Vnm = 0         # mean value of noise (like a bias value)
    Vnsd = 0.01    # standard deviation of noise (amplitude)

    # set initial state conditions
    # assume flywheel is spinning initially at known speed
    # x = [omega, theta]
    x0 = np.array([1, 0])
    # define the time array
    t = np.linspace(0,1,2001)
    sol = rk4fixed(flywheel, x0, t, args=(J, B, Ktach, Vnm, Vnsd))
    print('Plotting...')

    # Get the sensor output signals
    Vtach = np.zeros(len(t))
    for i in range(len(t)):
        _, y = flywheel(sol[i,:], t[i], J, B, Ktach, Vnm, Vnsd)
        Vtach[i] = y

    # Plot simulation results and signal output
    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    ax1.plot(t, sol[:,1]*180/math.pi, 'k', label='theta')
    ax1.legend(loc="upper right")
    ax1.set_ylabel('Position, degrees')
    ax2.plot(t, sol[:,0], 'k', label='omega')
    ax2.legend(loc="upper right")
    ax2.set_ylabel('Speed, rad/sec')
    ax3.plot(t, Vtach, 'k', label='Vtach')
    ax3.legend(loc="upper right")
    ax3.set_ylabel('Vtach, Volts')
    plt.xlabel('Time (sec)')
    plt.tight_layout()
    plt.show()
    # the following saves the plots to svg (or png)
    # plt.savefig("Raw_data_1_plots.svg")

    # Now save the Vtach data
    # Define the column headers as a comma-separated string
    # Save the array to a CSV file with the header
    # data = np.column_stack((t,Vtach))
    # headers = "Time (sec),Vtach (V)" # note: careful with spaces; only commas between items
    # np.savetxt('flywheel_decay_data_noisy.csv', data, delimiter=',', header=headers, comments='', fmt='%f')
    print("file created successfully.")

# Define some of the subroutines

# define the system ODEs
def flywheel(x, t, J, B, Ktach, Vnm, Vnsd):
    omega, theta = x[0], x[1]

    omega_dot = -B*omega/J
    theta_dot = omega

    # model sensor outputs
    # tachometer output voltage, with bias and noise
    Vnoise = np.random.normal(Vnm,Vnsd,1)
    #Vomega_tach = Ktach*omega + tach_bias + Vnoise*np.random()
    Vtach = Ktach*omega + Vnoise

	# specify outputs - model the sensor output
    y = Vtach

    return np.array([omega_dot, theta_dot]), y

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
