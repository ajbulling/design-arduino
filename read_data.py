import matplotlib.pyplot as plt
import numpy as np

myfile = open("data.txt", "r")
n = 1
data = []
for num in range(n):
    data.append(float(myfile.readline()))

t = np.arange(n)
plt.plot(t, data)
plt.show()

