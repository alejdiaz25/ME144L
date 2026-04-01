# ex4_scatter_plot.py
# 
# plt.scatter(x, y, - continued next line
# s=None, c=None, marker=None, cmap=None, norm=None,  - continued
# vmin=None, vmax=None, alpha=None, linewidths=None,  - continued
# verts=<deprecated parameter>, edgecolors=None, \*, - continued
# plotnonfinite=False, data=None, \*\*kwargs)
import matplotlib.pyplot as plt
import numpy as np
values = [1,2,3,4,5]
# using multiply from numpy
squares = np.multiply(values,values)
plt.scatter(values,squares, c='red', edgecolor='none', s = 40)
# use edgecolor = 'none' to remove outline

# set a chart title and label axes
plt.title("Square numbers", fontsize = 24)
plt.xlabel("Value", fontsize = 14)
plt.ylabel("Square of Value", fontsize = 14)
plt.tick_params(axis='both', labelsize = 14)
plt.show()

import sys
print(sys.version)