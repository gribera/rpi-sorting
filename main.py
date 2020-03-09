import cv2
import numpy as np
import colores as colores

class Main:
	color = colores.Colores()
	rects = []
	total = 0

	def __init__(self):
		self.color.start()

main = Main()