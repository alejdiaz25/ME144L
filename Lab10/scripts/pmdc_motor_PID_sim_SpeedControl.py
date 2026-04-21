# DSCLab
# PMDC motor model - Speed Control Comparison
# Ethan Rapp 11/27/20 v3
# PID using dt method
# updated 7-23-25 rgl (rk4fixed now includede; variables updated)
#

#%% Libraries
import numpy as np
import matplotlib.pyplot as plt
import math

plt.close('all')

def main():
    #%% Motor and Controller Variables
    # all parameter units in SI
    GR   = 45
    rm   = 0.0105  # [V/(rad/s)]
    Rm   = 30.6    # [Ohms]
    Vbus = 5       # [V]
    Bm   = 3.14e-7 # [N*m*s/rad]
    taumo   = 1.63e-4 # [N*m]
    Jm   = 0.5*0.009*(0.25/39.37)**2 # motor inertia, [kg*m^2], ignores gears
    # print("Jm = " + str(Jm))

    # Controller Gains
    Kp = 0.1     # P-control gain
    Ki = 0.00    # I-control gain
    Kd = 0.000   # D-control gain
    OLgain_P1 = 0.5 # [PWM/(rad/s)]

    #%% Simulation Variables
    # Time Vector
    t0 = 0
    tf = 15
    fs = 20   # [Hz], controller frequency - match to dataRate variable from exp.
    dt = 1/fs # [s]
    ts = np.arange(t0, tf, dt) # time array over dt

    # Initial Conditions
    wm0 = 0
    th0 = 0
    x0  = np.array([wm0, th0]) # initial condition

    #%% Set time and wm reference step values
    # wm reference
    wm_ref = []
    for i in range(len(ts)):
        tv = ts[i]
        if tv >= 1 and tv < 6:
            wm_ref.append(300)
        elif (tv >= 6) and (tv < 11):
            wm_ref.append(200)
        else:
            wm_ref.append(0)

    # Create empty lists to hold computed values
    wm_error = []
    PWMout   = []
    Xwm, Xth = [], []
    wm_exp = []
    th_exp = []
    Veq    = []
    sum_e  = 0
    e_last = 0

    #%% Run Simulation
    wm_last = wm0
    th_last = th0
    Xwm.append(wm0), Xth.append(th0), PWMout.append(0)
    wm_error.append(0)
    for i in range(0,len(ts)-1):
        # State and time vector
        th_exp.append(th_last)
        wm_exp.append(wm_last)
        x0 = [wm_last, th_last]
        
        N = 101 # Number of points used for RK4 solver
        tc = np.linspace(ts[i], ts[i+1], N) # step forward in time by dt; ts[i+1] = ts[i]+dt
        
        # Calculate Control Output
        e_wm  = wm_ref[i] - wm_last
        sum_e = sum_e + e_wm*dt
        dedt  = (e_wm - e_last)/dt
        
        # Feedforward
        # Option 1: use empirical relation between OLgain_P1 = PWM/speed
        # uff = OLgain_P1*wm_ref[i]
        # Option 2: use torque-speed curve model
        # uff = 255*(Vin)/Vb
        Vin = Rm*(taumo*math.tanh(wm_ref[i]/500)+Bm*wm_ref[i])/rm + rm*wm_ref[i]
        uff = 255*Vin/Vbus
        
        # PID Feedback
        u = Kp*e_wm + Ki*sum_e + Kd*dedt # PWM based on rad/sec

        uPWM = int(u + uff) # [PWM Int] from -255 to 255
        # watch for saturation
        if np.abs(uPWM)>255:
            uPWM = np.sign(uPWM)*255
        
        # Equivalent Voltage output
        Veq = (uPWM/255)*Vbus
        
        # Solve ODE for each Trange, then iterate loop
        sol = rk4fixed(pmdc, x0, tc, args=(rm, Rm, Bm, Jm, taumo, Veq))
        
        wm_last = sol[-1,0]
        th_last = sol[-1,1]
        Xwm.append(wm_last)
        Xth.append(th_last)
        PWMout.append(uPWM)
        wm_error.append(e_wm)

    #%% Figures
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    #ax1.step(t, vin, where='post')
    ax1.plot(ts, PWMout, '.-', label='PWM')
    ax1.legend(loc="upper right")
    ax1.set_ylabel('PWM [Int]')
    # ax1.set_ylim([-2,5])
    ax2.plot(ts, Xwm, '.-', label='wm')
    ax2.plot(ts, wm_ref, '--', label='wm_ref')
    ax2.set_ylabel('omega [rad/s]')
    ax2.legend(loc="upper right")
    # ax2.set_ylim([-10,250])
    ax3.plot(ts, wm_error, '.-', label='e_wm')
    ax3.set_ylabel('Error [rad/s]')
    ax3.legend(loc="upper right")
    # ax3.set_ylim([-400,400])
    ax3.set_xlabel('Time [s]')
    plt.tight_layout()
    plt.show()


#%% PMDC Motor ODEs
# define the system ODEs
def pmdc(x, t, rm, Rm, Bm, Jm, tauo, Vin):
    wmm, thetam = x[0], x[1]
    im = (Vin - rm*wmm)/Rm
    wmmdot    = (rm*im - Bm*wmm - tauo*np.tanh(wmm/1))/Jm
    thetamdot = wmm
    # specify outputs
    y = im
    return np.array([wmmdot, thetamdot]), y

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