#
# Two-can system simulation
# ME 144L Lab - updated spring 2026
#
import math
import numpy as np
import matplotlib.pyplot as plt

def main():
	# 
	 # Set initial volumes for can 1 and can 2
	V1o, V2o = 406, 0 # units of milliliters
	# Set simulation time parameters
	dt, t0, tf = 0.001, 0.0, 100
	N = math.floor(abs(tf-t0)/dt)
	x0 = np.array([V1o, V2o])
	t = np.linspace(0, tf, N)

	# Set K1 and K2 with proper units
	# Since Q = K*sqrt(V), then if Q is in ml/s 
	# then K must have units of sqrt(ml)/s
	# example values:
	K1, K2 = 1.295158671836755 , 0.4828403735337281
	sol1 = rk4fixed(two_can, x0, t, args=(K1, K2))
	V11 = sol1[:,0]
	V21 = sol1[:,1]
	# compute outputs
	Q11, Q21 = [], []
	for i in range(len(t)):
		_, y = two_can(sol1[i,:], t[i], K1, K2)
		Q11.append(y[0])
		Q21.append(y[1])

	print("Peak volume in V2 is :" + str(max(V21)))

	# run with ideal values 
	K1, K2 = 1.877055, 0.577013
	sol2 = rk4fixed(two_can, x0, t, args=(K1, K2))
	V12 = sol2[:,0]
	V22 = sol2[:,1]
	# compute outputs
	Q12, Q22 = [], []
	for i in range(len(t)):
		_, y = two_can(sol2[i,:], t[i], K1, K2)
		Q12.append(y[0])
		Q22.append(y[1])

	print("Peak volume in V2-ideal is :" + str(max(V22)))

	fig, (ax1, ax2) = plt.subplots(2)
	fig.suptitle('Two-can simulation')
	ax1.plot(t, V11, c='b', label='V1')
	ax1.plot(t, V21, c='b', label='V2')
	ax1.plot(t, V12, c='r', linestyle = 'dashed', label='V1-ideal')
	ax1.plot(t, V22, c='r', linestyle = 'dashed', label='V2-ideal')
	ax1.legend(loc="upper right")
	ax2.plot(t, Q11, c='b', label='Q1')
	ax2.plot(t, Q21, c='b', label='Q2')
	ax2.plot(t, Q12, c='r', linestyle = 'dashed', label='Q1-ideal')
	ax2.plot(t, Q22, c='r', linestyle = 'dashed', label='Q2-ideal')
	ax2.legend(loc="upper right")
	plt.xlabel('Time (sec)')
	plt.grid()
	plt.show()


# define the system ODEs
def two_can(x, t, K1, K2):
	V1, V2 = x[0], x[1]
	if V1 <= 0.0:
		Q1 = 0
	else:
		Q1 = K1*np.sqrt(abs(V1))

	if V2 <= 0.0:
		Q2 = 0
	else:
		Q2 = K2*np.sqrt(abs(V2))

	# specify outputs
	y = [Q1, Q2]

	return np.array([-Q1, +Q1-Q2]), y

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