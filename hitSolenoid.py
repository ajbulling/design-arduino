import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)

a = 1
while True:
	hit_file = open('hit.txt', 'r+')
	hit = hit_file.readline()
	if hit == 'hit':
		print(hit)
		GPIO.output(23, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(23, GPIO.LOW)
		hit_file.seek(0)
		hit_file.write('   ')
		hit_file.close()
		break
	hit_file.close()

