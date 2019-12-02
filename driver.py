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

# If you're looking for the code that was here it is now in
# broken_algorithm.py

# fqs_array is a python list of the data
fqs_array = []

# Creates the python list
for i in range(N // 2):
	fqs_array.append(l2d[0].get_ydata()[i])

# frq_response is a dictionary of freq:mag pairs
fqs_response = {i : fqs_array[i] for i in range(0, len(fqs_array))}

# Sorts based on magnitude (returns a list of tuples)
fqs_response = sorted(fqs_response.items(), key = lambda kv:(kv[1], kv[0]))

# Reverses so largest magnitude comes first
fqs_response = list(reversed(fqs_response))

# Remove first tuple (0 frequency)
fqs_response.pop(0)

# Filter out mirrored frequency data
i = 0
length = len(fqs_response)
while i < length:
    if fqs_response[i][0] > 1000 or fqs_response[i][0] < 150:
        fqs_response.pop(i)
        length -= 1
    else:
        i += 1

# Remove duplicate frequencies
interval = 20
i = 0
length = len(fqs_response)
# Start at first frequency, iterate through all of them (i is iterator)
while i < length:
    current_fq = fqs_response[i][0]
    j = i + 1
    # For each i, search through rest of list and remove duplicates
    while j < length:
        if abs(fqs_response[j][0] - current_fq) < interval:
            fqs_response.pop(j)
            length -= 1
        else:
            j += 1
    i += 1

# Take top 3 frequencies
fqs = []
for i in range(3):
    fqs.append(fqs_response[i][0])
print(fqs)

plt.grid()
plt.show()

