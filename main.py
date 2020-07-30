import numpy as np
import manager as manager

class Main:
	manager = manager.Manager()

	def __init__(self):
		self.manager.start('forma')

main = Main()