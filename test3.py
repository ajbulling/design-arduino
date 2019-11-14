from Adafruit_ADS1x15 import ADS1x15
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import numpy as np
import time

pga = 0256
sps = 860
adc = ADS1x15(ic=0x01)
adc.startContinuousConversion(0,pga,sps)
data = []
print("Go!")
for num in range(50000):
	data.append(adc.getLastConversionResults())
	#time.sleep(0.0001)
adc.stopContinuousConversion()
print("Done")

t = np.arange(50000)
plt.plot(t, data)
plt.show()

N = 50000
T = 1.0 / 50000.0
x = np.linspace(0.0, N*T, N)
yf = fft(data)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]))
plt.grid()
plt.show()

