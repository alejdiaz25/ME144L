#
# PMDC motor model
# R.G. Longoria 8-4-20 v1
# updated 7-23-25
import math
import numpy as np
import matplotlib.pyplot as plt

def main():
	# all parameter units in SI
	rm = 0.0107		# motor constant, N*m/A
	Rm = 30 		# motor armature resistance, ohms
	# below is an estimate of Jm based on the parts examined from
	# the dismantled motor; only the rotor and magnetic disc are included
	# total mass 9 grams, rough diameter 0.5 inch; model as equivalent disc
	Jm = 0.5*0.009*(0.25/39.37)**2		# motor inertia, kg*m^2, ignores gears
	print("Jm = " + str(Jm))
	GR = 48			# gear ratio
	Bm = 0.000178475e-3	# motor damping, from steady-state testing data
	taumo = 1*0.1838e-3 # coulombic bearing torque in motor; from ss testing data

	Vb = 4.5		# bus voltage
	ton, toff = 0.1, 1 		# turn on voltage

	dt, t0, tf = 0.001, 0.0, 1.5
	N = math.floor((tf-t0)/dt)
	x0 = np.array([0,0]) # initial values of omegam, and thetam
	t = np.linspace(0, tf, N)
	sol = rk4fixed(pmdc, x0, t, args=(rm, Rm, Bm, Jm, taumo, ton, toff, Vb))
	# compute outputs
	omega = sol[:,0] # rad/sec
	theta = 180*sol[:,1]/GR/math.pi # use thetam of motor to get output shaft in deg

	im = np.zeros(len(t))
	Vin = np.zeros(len(t))
	for i in range(len(t)):
		_, y = pmdc(sol[i,:], t[i], rm, Rm, Bm, Jm, taumo, ton, toff, Vb)
		im[i] = 1000*y[0] 	# current in mA
		Vin[i] = y[1]		# input voltage

	fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
	#Sfig.suptitle('PMDC simulation')
	ax1.plot(t, Vin, label=r'$V_{in}$')
	ax1.legend(loc="upper right")
	ax1.set_ylabel('Input voltage, V')
	ax2.plot(t, im, label=r'$i_m$')
	ax2.legend(loc="upper right")
	ax2.set_ylabel('Current, mA')
	ax3.plot(t, omega, label=r'$\omega$')
	ax3.set_ylabel('Speed, rad/sec')
	ax3.legend(loc="upper right")
	ax4.plot(t, theta, label=r'$\theta$')
	ax4.set_ylabel('Angle deg')
	ax4.legend(loc="upper right")
	plt.xlabel('Time (sec)')
	plt.tight_layout()
	plt.grid()
	plt.show()

# define the system ODEs
def pmdc(x, t, rm, Rm, Bm, Jm, tauo, ton, toff, Vb):
	# the two states are shaft speed and position
	omegam, thetam = x[0], x[1]

	# this model has a voltage that turns on and off
	if (t>ton) and (t<toff):
		Vinc = Vb
	else:
		Vinc = 0

	im = (Vinc - rm*omegam)/Rm
	omegamdot = (rm*im - Bm*omegam - tauo*np.sign(omegam))/Jm
	thetadot = omegam

	# specify outputs
	y = [im, Vinc]

	return np.array([omegamdot, thetadot]), y

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