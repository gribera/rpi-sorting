import cv2
import numpy as np
from collections import OrderedDict
import tracker as tracker

class Colores:
	blue_lower = np.array([100,100,23], np.uint8)
	blue_upper = np.array([125,255,255], np.uint8)

#	yellow_lower = np.array([15,100,20], np.uint8)
#	yellow_upper = np.array([45,255, 255], np.uint8)

	yellow_lower = np.array([20, 100, 100])
	yellow_upper = np.array([30, 255, 255])

	red1_lower = np.array([0,100,20], np.uint8)
	red1_upper = np.array([5,255,255], np.uint8)

	red2_lower = np.array([175,100,20], np.uint8)
	red2_upper = np.array([179,255,255], np.uint8)

	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)

	colores = ['blue', 'yellow', 'red']
	masks = [0, 0, 0]
	total = [0, 0, 0]
	border_colors = [(255,0,0), (0,255,255), (0,0,255)]

	def __init__(self):
		self.tracker = tracker.Tracker()

	def maskFrame(self, frameHSV):
		"""
			Crea las máscaras para cada color

			frameHSV: array, Frame convertido al espacio de color HSV
		"""
		masks = [0] * 3
		masks[0] = cv2.inRange(frameHSV, self.blue_lower, self.blue_upper)
		masks[1] = cv2.inRange(frameHSV, self.yellow_lower, self.yellow_upper)
		masks[2] = cv2.add(
				cv2.inRange(frameHSV, self.red1_lower, self.red1_upper),
				cv2.inRange(frameHSV, self.red2_lower, self.red2_upper)
			)
		combinedMasks = self.combineMasks(masks)
		return masks, combinedMasks

	def combineMasks(self, masks):
		"""
			Junta todas las máscaras en un solo frame.

			masks: array, Array con las máscaras de cada color.
		"""

		imgW, imgH = h, w = masks[0].shape
		result = np.zeros((imgW, imgH))

		for i in range(len(masks)):
			result += masks[i]

		result = result.clip(0, 255).astype("uint8")

		return result

	def getContours(self, frame, minArea=1000, returnMask=False):
		"""
			Recupera los contornos de los objetos de acuerdo a las máscaras de color.

			frame: array, Frame.
			minArea: int, Área mínima de los objetos a detectar
			returnMask: boolean, Indica si devuelve el frame o la máscara
		"""
		frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		masks, combinedMasks = self.maskFrame(frameHSV)

		finalContours = []
		for mask in range(len(masks)):
			_, contours, hierarchy = cv2.findContours(masks[mask], cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
			for cnt in contours:
				area = cv2.contourArea(cnt)
				if area > minArea:
					per = cv2.arcLength(cnt, True)
					poli = cv2.approxPolyDP(cnt, 0.02 * per, True)
					bbox = cv2.boundingRect(poli)

					finalContours.append([cnt, area, poli, bbox, mask])

		finalContours = sorted(finalContours, key = lambda x: x[1], reverse=True)

		if returnMask:
			return combinedMasks, finalContours
		else:
			return frame, finalContours
