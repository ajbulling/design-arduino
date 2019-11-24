from Adafruit_ADS1x15 import ADS1x15
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import scipy as sp
import time
import RPi.GPIO as GPIO

gains = [6144, 4096, 2048, 1024, 512, 256]
samples = [3300, 2400, 1600, 920, 490, 250, 128]
pga = gains[0]
sps = samples[0]
adc = ADS1x15(ic=0x01)
adc.startContinuousConversion(3,pga,sps)
data = []

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT)
GPIO.output(24,GPIO.LOW)  # GPIO Low

print("Go!")
N = sps


GPIO.output(24,GPIO.HIGH) # GPIO High
#time.sleep(0.05)
GPIO.output(24,GPIO.LOW)  # GPIO Low
print("Hit!")

# Read sensor data
time.sleep(0.25)
for num in range(N):
	data.append(adc.getLastConversionResults())
	#time.sleep(5 / N)
        '''
        if num == (N // 4):
            GPIO.output(24,GPIO.HIGH) # GPIO High
            time.sleep(0.1)
            GPIO.output(24,GPIO.LOW)  # GPIO Low
            print("Hit!")
            '''

adc.stopContinuousConversion()
print("Done")


filt_N = 1 #Filter order
Wn = 0.5  #cutoff frequency
B, A = signal.butter(filt_N, Wn, output='ba')
smooth_data = signal.filtfilt(B,A, data[:N//4])
t = np.arange(N//4)
plt.plot(t, data[:N//4])
plt.show()

plt.plot(smooth_data, 'b-')
plt.show()

T = 1.0 / N
yf = fft(smooth_data)
xf = np.linspace(0.0, 1.0/(2.0*T), N//4)
#yf = np.sin(50.0*2.0*np.pi*xf)
#yf = fft(yf)
l2d = plt.plot(xf, 2.0/N * np.abs(yf[0:N//4]))
plt.grid()
plt.show()

#Find fundamental frequency
max_freq = 0
x_index = 0
for i in range(200, 800):
    if l2d[0].get_ydata()[i] > max_freq:
        max_freq = l2d[0].get_ydata()[i]
        x_index = i

print("Frequency is " + str(x_index))

#Unhelpful so far

psd = np.abs(yf)**2
fftFreq = sp.fftpack.fftfreq(len(psd), 1. / 3300)
usableFreq = fftFreq > 0
plt.plot(fftFreq[usableFreq], 10* np.log(psd[usableFreq]))
plt.grid()

#plt.show()
