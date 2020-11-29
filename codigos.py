import cv2
import numpy as np
from pyzbar.pyzbar import decode
import tracker as tracker

class Codigos:
	def __init__(self):
		self.tracker = tracker.Tracker()

	def getContours(self, frame, minArea=1000, returnMask=False):
		finalContours = []

		for barcode in decode(frame):
			# print(barcode.data)
			# myData = barcode.data.decode('utf-8')
			# print(myData)
			poli = barcode.polygon
			poli = np.array([barcode.polygon], np.int32)
			poli = poli.reshape((-1, 1, 2))
			bbox = cv2.boundingRect(poli)
			# print(bbox)
			# print(type(bbox))
			# (x, y, w, h) =
			cnt = []
			area = []
			mask = []

			finalContours.append([cnt, area, poli, bbox, mask])

		return frame, finalContours
