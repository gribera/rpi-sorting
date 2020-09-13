import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

x = True
direccion = True

GPIO.output(26, 1);

while x == True:
    var = sys.stdin.readline().replace('\n', '')

    if var == 's':
    	break

    bits = 0
    for i in range(0, 3):
    	if var[i] == '0' or var[i] == '1':
    		bits += 1
    		print(var[i])


    if bits == 3:
    	GPIO.output(6, int(var[0]))
    	GPIO.output(13, int(var[1]))
    	GPIO.output(19, int(var[2]))
		# GPIO.output(13, False)
		# GPIO.output(19, False)


GPIO.cleanup()
