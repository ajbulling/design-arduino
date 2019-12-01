from Adafruit_ADS1x15 import ADS1x15
import time
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import scipy as sp
import datetime

pga = 6144
sps = 3300
adc = ADS1x15(ic = 0x00, debug=True)
N = 8192
data = []
hit_file = open('hit.txt', 'w')

mytime = datetime.datetime.now().strftime("%m-%d:%H:%M:%S")
filename = str(mytime) + '.txt'
log1 = open('log_unfiltered/' + filename, 'w')
log2 = open('log_filtered/' + filename, 'w')

adc.startContinuousDifferentialConversion(2, 3, pga, sps)
before = time.time()
for num in range (N):
    a = adc.getLastConversionResults()
    #a = adc.readADCDifferential(2, 3, pga, sps)
    data.append(a)
    log1.write(str(num) + '\t')
    log1.write(str(a) + '\n')
    if num == (N // 4):
	hit_file.write('hit')

after = time.time()
print("The total for loop time is: " + str( after - before))
print("Done")
log1.close()
hit_file.close()
adc.stopContinuousConversion()

filt_N = 1 #Filter order
Wn = 0.5  #cutoff frequency
B, A = signal.butter(filt_N, Wn, output='ba')
smooth_data = signal.filtfilt(B,A, data[:N//2])
t = np.arange(N//2)

plt.plot(t, data[:N//2])
plt.show()

plt.plot(t, smooth_data, 'b-')
plt.show()

T = 1.0 / N
yf = fft(smooth_data)
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

l2d = plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.grid()
plt.show()

#print(data)
