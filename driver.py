from Adafruit_ADS1x15 import ADS1x15
import RPi.GPIO as GPIO
import time
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import scipy as sp
import datetime
import os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)

gains = [6144, 4096, 2048, 1024, 512, 256]
samples = [3300, 2400, 1600, 920, 490, 250, 128]
pga = gains[2]
sps = samples[0]
adc = ADS1x15(ic = 0x00, debug=True)
N = sps * 4 # N is number of samples
data = []

mytime = datetime.datetime.now().strftime("%m-%d:%H:%M:%S")
filename = str(mytime) + '.txt'
log1 = open('log_unfiltered/' + filename, 'w')
log2 = open('log_filtered/' + filename, 'w')

#adc.startContinuousDifferentialConversion(0, 1, pga, sps)
adc.startContinuousConversion(0, pga, sps)

#Activate solenoid
GPIO.output(23, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(23, GPIO.LOW)
time.sleep(0.35)

before = time.time()
# Start collecting data
for num in range (N):
    a = adc.getLastConversionResults()
    data.append(a)
after = time.time()
'''
for i in range(len(data)):
    log1.write(str(i) + '\t')
    log1.write(str(data[i]) + '\n')
'''

timeTaken = after - before
sampleRate = N / timeTaken

#print("The total for loop time is: " + str( timeTaken ))
log1.close()
adc.stopContinuousConversion()

filt_N = 1 #Filter order
Wn = 0.5  #cutoff frequency
B, A = signal.butter(filt_N, Wn, output='ba')
smooth_data = signal.filtfilt(B,A, data[:len(data)//2])

t = np.arange(len(data)//2)

# Plot unfiltered data
plt.plot(t, data[:len(data)//2])
plt.show()

# Plot filtered data
#plt.plot(t, smooth_data, 'b-')
#plt.show()

# Perform FFT
T = 1.0 / sampleRate
yf = fft(smooth_data)
#yf = fft(data)
# Decreasing size by one to avoid spike at zero frequency
xf = np.linspace(1.0, 1.0/(2.0*T), N//2 - 1)
l2d = plt.plot(xf, 2.0/sampleRate * np.abs(yf[1:N//2]))

# If you're looking for the code that was here it is now in
# broken_algorithm.py

fqs_array = []
mag_array = []

# Populates the lists with frequency and magnitude data
for i in range(N // 2 - 1):
    fqs_array.append(l2d[0].get_xdata()[i])
    mag_array.append(l2d[0].get_ydata()[i])

# fqs_response_dictionary is a dictionary of freq:mag pairs
#fqs_response = {i : fqs_array[i] for i in range(0, len(fqs_array))}
fqs_response_dictionary = {fqs_array[i] : mag_array[i] for i in range(0, len(fqs_array))}

# Sorts based on magnitude (returns a list of tuples)
fqs_response = sorted(fqs_response_dictionary.items(), key = lambda kv:(kv[1], kv[0]))

# Reverses so largest magnitude comes first
fqs_response = list(reversed(fqs_response))

# Remove first tuple (0 frequency)
fqs_response.pop(0)

# Filter out "mirrored" frequency data
i = 0
length = len(fqs_response)
while i < length:
    if fqs_response[i][0] > 500 or fqs_response[i][0] < 100:
        fqs_response.pop(i)
        length -= 1
    else:
        i += 1

# Remove duplicate frequencies
interval = 15 # If within 15 Hz, ignore
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

# Grab top 3 frequencies and magnitudes
fqs = []
mags = []
for i in range(4):
    # Ignore all data with magnitude less than 0.15
    if fqs_response[i][1] < 0.15:
        fqs.append(0)
        mags.append(0)
    else:
        fqs.append(fqs_response[i][0])
        mags.append(fqs_response[i][1])
print("Found frequencies:")
print(fqs)

# Find liquid level
# Expected frequency values for various kegs
full_fqs = [197, 104, 134, 283, 269, 499, 399]
#full_fqs = [117, 269, 357]
three_fourths_fqs = [225,154, 325, 127, 443, 117, 294]
one_half_fqs = [152, 190, 167, 400]
one_fourth_fqs = [207, 252, 413, 226, 337 , 384]
empty_fqs = [260, 370, 432]

# First index is full keg, last index is empty keg
mag_list = [0, 0, 0, 0, 0]
# Mapping of indices to levels for mag_list
lqd_lvl_map = {0 : "100%", 1 : "75%", 2 : "50%", 3 : "25%", 4 : "0%"}

# Figure out most likely liquid level
for actual_fq in fqs:
    for expected_fq in full_fqs:
        if abs(expected_fq - actual_fq) < 5:
            mag_list[0] += fqs_response_dictionary[actual_fq]
    for expected_fq in three_fourths_fqs:
        if abs(expected_fq - actual_fq) < 5:
            mag_list[1] += fqs_response_dictionary[actual_fq]
    for expected_fq in one_half_fqs:
        if abs(expected_fq - actual_fq) < 5:
            mag_list[2] += fqs_response_dictionary[actual_fq]
    for expected_fq in one_fourth_fqs:
        if abs(expected_fq - actual_fq) < 5:
            mag_list[3] += fqs_response_dictionary[actual_fq]
    for expected_fq in empty_fqs:
        if abs(expected_fq - actual_fq) < 5:
            mag_list[4] += fqs_response_dictionary[actual_fq]

# Take highest count and map to liquid level
highest_count = 0
lqd_lvl = ''
for i in range(len(mag_list)):
    if mag_list[i] >= highest_count:
        highest_count = mag_list[i]
        lqd_lvl = lqd_lvl_map[i]

# Removes 1/2, 3/4, and Full from the possibilities of being chosen
# if magnitude is less than 1 (less than half)
if highest_count < 1:
    if mag_list[3] > mag_list[4]:
        lqd_lvl = lqd_lvl_map[3]
    else:
        lqd_lvl = lqd_lvl_map[4]

print("Magnitude sum: " + str(highest_count))
print("Liquid level: " + lqd_lvl)

# Write liquid level to file
level_file = open('level.txt', 'w')
level_file.write(str(lqd_lvl))
level_file.close()

# Upload level to the http server (remove -s for more verbose output)
os.system("curl -s --upload-file level.txt 68.180.48.172:8000")

# Write over file to give a "clean slate" for next time
level_file = open('level.txt', 'w')
level_file.seek(0)
level_file.write("    ")
level_file.close()

# Show FFT
plt.grid()
plt.show()

