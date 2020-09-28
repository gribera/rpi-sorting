import sys
import RPi.GPIO as GPIO

class Cinta:
	direccion = True
	velocidades = [
		[0, 0, 0],
		[0, 0, 1],
		[0, 1, 0],
		[0, 1, 1],
		[1, 0, 0],
		[1, 0, 1],
		[1, 1, 0],
		[1, 1, 1]
	]

	def __init__(self):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(6, GPIO.OUT)
		GPIO.setup(13, GPIO.OUT)
		GPIO.setup(19, GPIO.OUT)
		GPIO.setup(26, GPIO.OUT)

	def setDireccion(self):
		self.direccion = not self.direccion
		GPIO.output(26, self.direccion)

	def setVelocidad(self, velocidad):
		GPIO.output(6, self.velocidades[int(velocidad)][0])
		GPIO.output(13, self.velocidades[int(velocidad)][1])
		GPIO.output(19, self.velocidades[int(velocidad)][2])
