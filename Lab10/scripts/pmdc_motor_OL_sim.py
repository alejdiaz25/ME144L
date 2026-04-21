# PMDC motor model open-loop control simulation
# R.G. Longoria 8-2-24 v2
# updated 7-23-22 rgl
# includes rk4fixed and ODEs at end
# Lab 10 prelab edits by Alejandro Diaz:
#   - motor parameters updated to Lab 9 values
#   - PWM array added and plotted as a 4th subplot (order: PWM, Vin, omega, error)
#   - figure saved to ../images/
import os
import math
import numpy as np
import matplotlib.pyplot as plt

def main():
    # all parameter units in SI -- values from Lab 9 steady-state testing
    rm = 1.011e-2	# motor constant, N*m/A
    Rm = 26.9 		# motor armature resistance, ohms
    Bm = 4.71e-7	# motor damping
    Jm = 0.5*0.009*(0.25/39.37)**2	# motor inertia, kg*m^2, ignores gears
    # print("Jm = " + str(Jm))
    GR = 45			# gear ratio
    taumo = 9.81e-5 # coulombic bearing torque in motor

    # This code simulates a simple experiment where you want to drive the motor in open-loop
    # and let it run over a time interval so the output shaft turns by a desired amount.
    # If the model relation works well, then the speed is achieved and so is the
    # desired angular displacement.

    # 1. Choose a speed. For the motor tested, it was found that a minimum PWM level is needed
    # for the motor to 'un-stick', or to overcome 'stiction'. At this PWM, a measured PWM-speed
    # correlation will reveal the speed (e.g., 182 rad/sec, or 29 rev/sec).
    # Set this as a 'desired' speed, omega_d
    # Lab 10 prelab: sweep three values matching Lab 9 experimental points:
    #   340.34 rad/s -> exp PWM 230 (3250 RPM)
    #   212.59 rad/s -> exp PWM 155 (2030 RPM)
    #    90.06 rad/s -> exp PWM  80 ( 860 RPM)
    omega_d = 212.59 # desired or reference speed in rad/sec
    # Note 1: The lowest speed value is chosen here to maximize the time interval for turning
    # the shaft by a given amount
    # 2. Set the *motor* angle interval to turn in this simulation
    theta_motor = 180 # degrees
    theta_d = theta_motor*GR # this is desired motor shaft angle times the GR to give motor shaft
    # angle in degrees
    # 3. Solve for the time interval to achived theta_d, assuming you are turning at the
    # desired (constant) speed omega_d
    Tinterval = (theta_d*math.pi/180)/omega_d
    # this is an approximation; ignores rise time / fall time.
    print(f"Time interval to achieve {theta_d:.2f} deg is {Tinterval:.2f} seconds")

    # 4. Set the simulation parameters. Turn on at ton, add Tinterval to get toff
    ton = 0.1
    toff = ton + Tinterval
    tend = 3 # time in seconds to run the 'big loop', should be larger than toff

    # set up for simulation
    dt = 0.05 # set the time step, 50 ms (similar to Arduino implementation)
    N = math.floor(tend/dt)
    t = np.linspace(0,tend,N)
    # Create arrays for saving data
    Vin = np.zeros(len(t))
    PWM = np.zeros(len(t))
    im = np.zeros(len(t))
    omega = np.zeros(len(t))
    theta = np.zeros(len(t))
    e_omega = np.zeros(len(t))
    omegar = np.zeros(len(t))

    #sum_ev = np.zeros(len(t)) # needed for discrete PID I control

    Vb = 4.82       # bus voltage, based on power supply or battery voltage (Lab 9)
    # control loop

    i = 1 # loop index
    tc, Vinc, imc, omegac, thetac, omegarc, e_omegac = 0, 0, 0, 0, 0, 0, 0 # initial conditions
    # save all these initial values
    t[0], Vin[0], im[0], omega[0], theta[0], omegar[0], e_omega[0] = tc, Vinc, imc, omegac, thetac, omegarc, e_omegac

    # The while loop below runs and takes time steps 'dt'
    # choose dt to experiment with the time step you would take in the Arduino loop
    # the loop first determines the PWM (here using mcc for PWM)
    # In Arduino PWM for the H-bridge driver used ranges from -255 to 255
    # here, we model this with mcc which ranges from -1 to 1 to modify bus voltage vb.
    # The key difference in this simulation from other simulations is that we don't
    # just simulate over some time range. Rather, we simulate with RK4 fixed over each
    # time interval, dt. So you need to keep updating the initial conditions. Then,
    # we just keep the last point at the end of the small interval of dt.
    # The values at the end of each dt are saved in the arrays initialized.

    while tc < 2:
    	# determine next step
        if (tc>ton) and (tc<toff):
            # look at slides to get explanation for this next line:
            omega_r = omega_d
            mcc = (Rm*(taumo*np.tanh(omega_d)+Bm*omega_d)/rm + rm*omega_d)/Vb
        else:
            mcc = 0
            omega_r = 0

        # Simple model of H-bridge voltage conversion
        omegar[i] = omega_r # store the reference value of omega for plotting
        Vinc = mcc*Vb # this is voltage input to armature of motor
        PWM[i] = mcc*255 # integer-equivalent PWM command for the H-bridge

        # Mow, run a simulation over interaval dt with the vinc held constant
        # In a control loop, this is what you would do: you'd compute a command
        # then send it to the motor drive; it would then run over the 'loop time'
        # with this constant command
        # Here we run an RK4 simulation of the pmdc motor over that dt to capture
        # the dynamics of the system resulting from that command
        to = tc # set the initial time
        tend = to + dt # the final time is dt later
        x0 = np.array([omegac, thetac]) # set initial conditions for this interval
        N = 100 # choose how many steps over dt for RK4 simulation. Can adjust.
        ts = np.linspace(to, tend, N) # time array over dt
        # call the RK4
        sol = rk4fixed(pmdc, x0, ts, args=(rm, Rm, Bm, Jm, taumo, Vinc))
        # now, we don't want all the results, just what is at the end of the dt
        N = len(ts)
        omegac = sol[N-1,0] # grab the value of omega at end of dt
        thetac = sol[N-1,1] # grab the value of theta at end of dt
        tc = ts[N-1] # grab the time value - we know this, of course
        # now start storing these away so we can plot them later
        omega[i] = omegac # store motor shaft speed, rad/sec
        theta[i] = 180*thetac/GR/math.pi # store output shaft angle, deg
        t[i] = tc # store the time value
        e_omega[i] = omega_r-omegac # error in omega
        # grab any outputs defined in the function
        # here the current and input voltage are outputs
        _, y = pmdc(sol[N-1,:], ts[N-1], rm, Rm, Bm, Jm, taumo, Vinc)

        im[i] = 1000*y 	# store current at end of interval, mA
        Vin[i] = Vinc	# store input voltage, volts

        # increment the loop index
        i += 1

    # end of big simulation loop

    # Now plot the stored results
    fig1, (ax0, ax1, ax2, ax3) = plt.subplots(4)
    ax0.plot(t, PWM, '.-', label='PWM')
    ax0.legend(loc="upper right")
    ax0.set_ylabel('PWM [int]')
    ax0.set_ylim([-20,280])
    ax1.plot(t, Vin, '.-', label=r'$V_{in}$')
    ax1.legend(loc="upper right")
    ax1.set_ylabel('Input voltage, V')
    ax1.set_ylim([-2,5])
    ax2.plot(t, omega, '.-', label=r'$\omega$')
    ax2.plot(t, omegar, '--', label=r'$\omega_r$')
    ax2.set_ylabel('Speed, rad/sec')
    ax2.legend(loc="upper right")
    ax2.set_ylim([-10,400])
    ax3.plot(t, e_omega, '.-', label=r'$e_{\omega}$')
    ax3.set_ylabel('Error rad/sec')
    ax3.legend(loc="upper right")
    ax3.set_ylim([-400,400])
    ax3.set_xlabel('Time (sec)')
    plt.tight_layout()
    # Save the figure to ../images/ keyed by omega_d (RPM) so repeated
    # runs at different desired speeds do not overwrite each other
    img_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images"))
    os.makedirs(img_dir, exist_ok=True)
    rpm_tag = int(round(omega_d*60.0/(2*math.pi)))
    fig1.savefig(os.path.join(img_dir, f"ol_sim_w{rpm_tag}rpm.png"), dpi=200)
    plt.show()

    # the following is a plot of the angular position of the
    # output shaft
    fig2 = plt.figure(2)
    plt.plot(t[1:i-1],theta[1:i-1],'.-', label=r'$\theta$')
    plt.ylabel('Angular position, deg')
    plt.xlabel('Time (sec)')
    fig2.savefig(os.path.join(img_dir, f"ol_sim_theta_w{rpm_tag}rpm.png"), dpi=200)
    plt.show()

# define the system ODEs
def pmdc(x, t, rm, Rm, Bm, Jm, tauo, Vin):
    omegam, thetam = x[0], x[1]
    # input to this model in input voltage Vin
    im = (Vin - rm*omegam)/Rm
    omegamdot = (rm*im - Bm*omegam - tauo*np.tanh(omegam/60))/Jm
    thetamdot = omegam
    # specify outputs

    y = im

    return np.array([omegamdot, thetamdot]), y

# RK4 fixed-step
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
