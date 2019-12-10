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

gains = [6144, 4096, 2048, 1024, 512, 256]
samples = [3300, 2400, 1600, 920, 490, 250, 128]
pga = gains[2]
sps = samples[0]
adc = ADS1x15(ic = 0x00, debug=True)
N = sps * 4
data = []

mytime = datetime.datetime.now().strftime("%m-%d:%H:%M:%S")
filename = str(mytime) + '.txt'
log1 = open('log_unfiltered/' + filename, 'w')
log2 = open('log_filtered/' + filename, 'w')

#adc.startContinuousDifferentialConversion(0, 1, pga, sps)
adc.startContinuousConversion(0, pga, sps)

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

plt.plot(t, data[:len(data)//2])
plt.show()

#plt.plot(t, smooth_data, 'b-')
#plt.show()

T = 1.0 / sampleRate
yf = fft(smooth_data)
#yf = fft(data)
# Decreasing size by one to avoid spike at zero frequency
xf = np.linspace(1.0, 1.0/(2.0*T), N//2 - 1)
l2d = plt.plot(xf, 2.0/sampleRate * np.abs(yf[1:N//2]))

# If you're looking for the code that was here it is now in
# broken_algorithm.py

# fqs_array is a python list of the data
fqs_array = []
mag_array = []

# Creates the python lists for frequencies and mags
for i in range(N // 2 - 1):
    fqs_array.append(l2d[0].get_xdata()[i])
    mag_array.append(l2d[0].get_ydata()[i])

# frq_response is a dictionary of freq:mag pairs
#fqs_response = {i : fqs_array[i] for i in range(0, len(fqs_array))}
fqs_response_dictionary = {fqs_array[i] : mag_array[i] for i in range(0, len(fqs_array))}

# Sorts based on magnitude (returns a list of tuples)
fqs_response = sorted(fqs_response_dictionary.items(), key = lambda kv:(kv[1], kv[0]))

# Reverses so largest magnitude comes first
fqs_response = list(reversed(fqs_response))

# Remove first tuple (0 frequency)
fqs_response.pop(0)

# Filter out mirrored frequency data
i = 0
length = len(fqs_response)
while i < length:
    if fqs_response[i][0] > 500 or fqs_response[i][0] < 100:
        fqs_response.pop(i)
        length -= 1
    else:
        i += 1

# Remove duplicate frequencies
interval = 15
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
mags = []
for i in range(4):
    if fqs_response[i][1] < 0.15:
        fqs.append(0)
        mags.append(0)
    else:
        fqs.append(fqs_response[i][0])
        mags.append(fqs_response[i][1])
print(fqs)

# Find liquid level
fund_frq = fqs[0]
full_fqs = [197, 104, 134, 283, 269, 499, 399]
#full_fqs = [117, 269, 357]
three_fourths_fqs = [225,154, 325, 127, 443, 117, 294]
one_half_fqs = [152, 190, 167, 400]
one_fourth_fqs = [207, 252, 413, 226, 337 , 384]
empty_fqs = [260, 370, 432]

# First index is full keg, last index is empty keg
count_list = [0, 0, 0, 0, 0]
lqd_lvl_map = {0 : "100%", 1 : "75%", 2 : "50%", 3 : "25%", 4 : "0%"}

# Figure out most likely liquid level
for actual_fq in fqs:
    for expected_fq in full_fqs:
        if abs(expected_fq - actual_fq) < 5:
            count_list[0] += fqs_response_dictionary[actual_fq]
    for expected_fq in three_fourths_fqs:
        if abs(expected_fq - actual_fq) < 5:
            count_list[1] += fqs_response_dictionary[actual_fq]
    for expected_fq in one_half_fqs:
        if abs(expected_fq - actual_fq) < 5:
            count_list[2] += fqs_response_dictionary[actual_fq]
    for expected_fq in one_fourth_fqs:
        if abs(expected_fq - actual_fq) < 5:
            count_list[3] += fqs_response_dictionary[actual_fq]
    for expected_fq in empty_fqs:
        if abs(expected_fq - actual_fq) < 5:
            count_list[4] += fqs_response_dictionary[actual_fq]

# Take highest count and map to liquid level
highest_count = 0
lqd_lvl = ''
for i in range(len(count_list)):
    if count_list[i] >= highest_count:
        highest_count = count_list[i]
        lqd_lvl = lqd_lvl_map[i]

#Removes 1/2, 3/4, and Full from the possibilities of being chosen
if highest_count < 1:
    if count_list[3] > count_list[4]:
        lqd_lvl = lqd_lvl_map[3]
    else:
        lqd_lvl = lqd_lvl_map[4]
        # If no good frequency data, must be an empty keg
'''
empty_count = 0
for each in mags:
    if each < 1:
        empty_count += 1
if empty_count == 3:
    lqd_lvl = "0%"
'''
print("Confidence: " + str(highest_count))
print(lqd_lvl)
'''
if abs(fund_frq - 200) < 5:
    print("100%")
elif abs(fund_frq - 225) < 5:
    print("75%")
elif abs(fund_frq - 166) < 5:
    print("50%")
elif abs(fund_frq - 250) < 5 or abs(fqs[1] -250) < 5:
    print("25%")
else:
    print("0%")
'''
'''
level = 54 # Hard-coded, fix later
level_file = open('level.txt', 'w')
level_file.write(str(level))
os.system("curl --upload-file level.txt 68.180.48.172:8000")
level_file.close()
'''
plt.grid()
plt.show()

