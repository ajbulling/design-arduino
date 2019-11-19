from Adafruit_ADS1x15 import ADS1x15
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import time
import RPi.GPIO as GPIO

pga = 0256
sps = 860
adc = ADS1x15(ic=0x01)
adc.startContinuousConversion(0,pga,sps)
data = []

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT)

print("Go!")
N = sps * 10

# Read sensor data
for num in range(N):
	data.append(adc.getLastConversionResults())
	time.sleep(5 / N)
        if num == (N // 4):
            GPIO.output(24,GPIO.HIGH) # GPIO High
            time.sleep(0.05)
            GPIO.output(24,GPIO.LOW)  # GPIO Low

adc.stopContinuousConversion()
print("Done")


filt_N = 3 #Filter order
Wn = 0.1  #cutoff frequency
B, A = signal.butter(filt_N, Wn, output='ba')
smooth_data = signal.filtfilt(B,A, data)
t = np.arange(N)
plt.plot(t, data)
plt.show()

plt.plot(smooth_data, 'b-')
plt.show()

T = 1.0 / N
yf = fft(data)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]))
plt.grid()
plt.show()

