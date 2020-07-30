import numpy as np
import manager as manager

class Main:
	manager = manager.Manager('forma')

	def __init__(self):
		self.manager.start()

main = Main()