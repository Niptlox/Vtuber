import numpy
import numpy as np
from scipy.interpolate import splrep, BSpline


def smoothListGaussian(list, degree=5):
    window = degree * 2 - 1
    weight = numpy.array([1.0] * window)
    weightGauss = []
    for i in range(window):
        i = i - degree + 1
        frac = i / float(window)
        gauss = 1 / (numpy.exp((4 * (frac)) ** 2))
        weightGauss.append(gauss)
    weight = numpy.array(weightGauss) * weight
    smoothed = [0.0] * (len(list) - window)
    for i in range(len(smoothed)):
        smoothed[i] = sum(numpy.array(list[i:i + window]) * weight) / sum(weight)
    return smoothed


def np_smooth(arr, cof=4):
    if cof == 1:
        return arr
    n = len(arr)
    x = np.arange(0, n)
    tck = splrep(x, arr, s=0)
    xnew = np.arange(0, n-1, 1 / cof)
    return BSpline(*tck)(xnew)


if __name__ == '__main__':
    # x = np.arange(0, 2 * np.pi + np.pi / 4, 2 * np.pi / 16)
    x = np.arange(0, 5)
    rng = np.random.default_rng()
    y = np.array([3, 6, 8, 2, 1])
    # y = np.sin(x) + 0.4 * rng.standard_normal(size=len(x))

    tck = splrep(x, y, s=0)
    tck_s = splrep(x, y, s=len(x))

    import matplotlib.pyplot as plt

    xnew = np.arange(0, 5, 1 / 4)

    # plt.plot(xnew, np.sin(xnew), '-.', label='sin(x)')
    plt.plot(xnew, np_smooth(y), '-', label='s=0')
    plt.plot(xnew, BSpline(*tck_s)(xnew), '-', label=f's={len(x)}')
    plt.plot(x, y, 'o')
    plt.legend()
    plt.show()
