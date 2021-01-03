import numpy as np
import manager as manager
import server as server

class Main:
	server = server.Server()

	def __init__(self):
		"""
			Constructor.
		"""
		self.server.start()

main = Main()