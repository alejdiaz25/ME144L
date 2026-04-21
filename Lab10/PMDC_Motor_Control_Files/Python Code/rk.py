# Fixed-step RK algorithms
# call by using rk.rkNfixed, where N = 1, 2, or 4 (order)
def rk1fixed(f, x0, t, args=()):
    import numpy
    N = len(t)
    x = numpy.zeros((N, len(x0)))
    x[0] = x0
    for i in range(N - 1):
        k1, _ = f(x[i], t[i], *args)
        x[i+1] = x[i] + (t[i+1] - t[i]) * k1
    return x

def rk2fixed(f, x0, t, args=()):
    import numpy
    N = len(t)
    x = numpy.zeros((N, len(x0)))
    x[0] = x0
    for i in range(N - 1):
        h = t[i+1] - t[i]
        k1, _ = f(x[i], t[i], *args)
        k2, _ = f(x[i] + k1 * h / 2., t[i] + h / 2., *args)
        x[i+1] = x[i] + h * k2
    return x

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
