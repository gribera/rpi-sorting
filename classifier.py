import serial

class Classifier:
	port = None

	def __init__(self):
		self.port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.5)

	def classify(self, target):
		self.port.write(str(target).encode())