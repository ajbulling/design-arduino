import serial
import RPi.GPIO as GPIO
import time

ser=serial.Serial("/dev/ttyACM0", 9600, timeout=3)
ser.baudrate=9600
ser.flushInput()
print("start")
#cmd = "012345688902341"
#ser.write(cmd.encode())
for num in range(50):
    ser.write('1\n')
ser.flushInput()
msg = ser.readlines(30)
print(msg)
#s = ser.readlines(1000)
#print(s)

