import cv2
import numpy as np
from pyzbar.pyzbar import decode
import tracker as tracker

class Codigos:
	knownObjects = [[], []]

	def __init__(self):
		"""
			Constructor.
		"""
		self.tracker = tracker.Tracker()

	def getContours(self, frame, minArea=1000, returnMask=False):
		"""
			Detecta los contornos de los objetos.

			frame: array, Frame
			minArea: int, Área mínima de detección (1000 por defecto).
			returnMask: boolean, Devuelve máscara en lugar del frame
		"""
		finalContours = []

		for barcode in decode(frame):
			poli = barcode.polygon
			poli = np.array([barcode.polygon], np.int32)
			poli = poli.reshape((-1, 1, 2))
			bbox = cv2.boundingRect(poli)
			txt = barcode.data.decode('utf-8')

			finalContours.append([None, None, poli, bbox, txt])

		if returnMask:
			mask = cv2.inRange(frame, (0, 0, 0), (200, 200, 200))
			thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
			inverted = 255 - thresholded
			return inverted, finalContours
		else:
			return frame, finalContours

	def getKnownObjects(self):
		"""
			Devuelve los objetos reconocidos por esta clase.
		"""
		return self.knownObjects