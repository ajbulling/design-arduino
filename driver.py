from Adafruit_ADS1x15 import ADS1x15
import RPi.GPIO as GPIO
import time
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import scipy as sp
import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)

pga = 6144
sps = 3300
adc = ADS1x15(ic = 0x00, debug=True)
N = sps * 2
data = []
hit_file = open('hit.txt', 'w')

mytime = datetime.datetime.now().strftime("%m-%d:%H:%M:%S")
filename = str(mytime) + '.txt'
log1 = open('log_unfiltered/' + filename, 'w')
log2 = open('log_filtered/' + filename, 'w')

adc.startContinuousDifferentialConversion(2, 3, pga, sps)
#adc.startContinuousConversion(2, pga, sps)

GPIO.output(23, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(23, GPIO.LOW)

time.sleep(0.25)
before = time.time()
for num in range (N):
    a = adc.getLastConversionResults()
    #a = adc.readADCSingleEnded(2, pga, sps)
    #a = adc.readADCDifferential(2, 3, pga, sps)
    data.append(a)
'''
    if num == (N // 4):
	print('Hit!')
	GPIO.output(23, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(23, GPIO.LOW)
'''
after = time.time()
for i in range(N):
    log1.write(str(i) + '\t')
    log1.write(str(data[i]) + '\n')

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

#plt.plot(t, smooth_data, 'b-')
#plt.show()

T = 1.0 / N
yf = fft(smooth_data)
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

l2d = plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))

mags = [-1000, -2000, -3000]
fqs = [-1000, -2000, -3000]

def is_duplicate(current_mag, i):
	# Loops through the magnitudes/frequencies and replaces them
	# if a higher magnitude within the range of interval of indexes is found
	interval = 10
	for index in range(3):
		if current_mag > mags[index] and (i - fqs[index]) < interval:
			'''
			print("Current mag is " + str(current_mag))
			print("Current frequency is " + str(i))
			#print("Saved magnitude is " + str(mags[index]))
			print("Magnitudes are ", mags)
			#print("Saved frequency is " + str(fqs[index]))
			print("Frequencies are ", fqs)
			print("index is " + str(index))
			print('\n')
			if index == 2 and current_mag < mags[1]:
				mags[index] = current_mag
				fqs[index] = i
			elif index == 2 and current_mag < mags[0]:
			'''
			return True
		# Returns true if we see a frequency value close to one of the
		# saved frequencies but with a lower magnitude, else returns false
		if (abs(fqs[index] - i) < interval):
			return True
	return False

mags = [-1000, -2000, -3000]
fqs = [-1000, -2000, -3000]
for i in range(50, 1000):
    if is_duplicate(l2d[0].get_ydata()[i], i):
	continue
    if l2d[0].get_ydata()[i] > mags[0]:
	mags[2] = mags[1]
	mags[1] = mags[0]
        mags[0] = l2d[0].get_ydata()[i]
	fqs[2] = fqs[1]
	fqs[1] = fqs[0]
        fqs[0] = i
    elif l2d[0].get_ydata()[i] > mags[1]: 
	mags[2] = mags[1]
        mags[1] = l2d[0].get_ydata()[i]
	fqs[2] = fqs[1]
        fqs[1] = i
    elif l2d[0].get_ydata()[i] > mags[2]:
        mags[2] = l2d[0].get_ydata()[i]
        fqs[2] = i
print(mags)
print("Frequency 1 is " + str(fqs[0]))
print("Frequency 2 is " + str(fqs[1]))
print("Frequency 3 is " + str(fqs[2]))

# Data_array is a python list of the data
data_array = []

# Creates the python list
for i in range(N // 2):
	data_array.append(l2d[0].get_ydata()[i])

# mydata is a dictionary of freq:mag pairs
mydata = {i : data_array[i] for i in range(0, len(data_array))}
# Sorts based on magnitude
mydata = sorted(mydata.items(), key = lambda kv:(kv[1], kv[0]))
# Reverses so largest magnitude comes first
mydata = list(reversed(mydata))
for i in range(25):
	print(mydata[i])

#peaks, props = signal.find_peaks(l2d[0].get_ydata(), distance=10)
#print(peaks)

plt.grid()
plt.show()

