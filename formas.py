import cv2
import numpy as np
from collections import OrderedDict
import tracker as tracker

class Formas:
	def __init__(self):
		self.tracker = tracker.Tracker()

	def findDis(self, pts1, pts2):
		return (((pts2[0]-pts1[0])**2 + (pts2[1]-pts1[1])**2)**0.5)/10

	def detectShape(self, pts):
		forma = ''
		if (pts == 3):
			forma = 'Triangulo'
		elif (pts == 4):
			forma = 'Cuadrado'
		elif (pts > 6):
			forma = 'Circulo'
		else:
			forma = 'Indefinido'

		return forma

	def getContours(self, img, minArea = 1000, filter=0, draw=True):
		"""
			Recupera los contornos de los objetos encontrados utilizando Canny.

			img: array, Frame.
			minArea: int, Área mínima de los objetos a detectar
			filter: int, Filtro de cantidad de bordes (detecta contornos con la
													   cantidad de bordes especificada)
			draw: bool, Muestra los bordes
		"""
		imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)

		imgCanny = cv2.Canny(imgBlur, 11, 100)

		kernel = np.ones((5,5))
		imgDil = cv2.dilate(imgCanny, kernel, iterations=3)
		imgThre = cv2.erode(imgDil, kernel, iterations=2)

		_, contours, hierarchy = cv2.findContours(imgThre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		finalContours = []
		for cnt in contours:
			area = cv2.contourArea(cnt)
			if area > minArea:
				per = cv2.arcLength(cnt, True)
				poli = cv2.approxPolyDP(cnt, 0.02 * per, True)
				bbox = cv2.boundingRect(poli)
				if filter > 0:
					if len(poli) == filter:
						finalContours.append([cnt, area, poli, bbox, None])
				else:
					finalContours.append([cnt, area, poli, bbox, None])

				finalContours = sorted(finalContours, key = lambda x: x[1], reverse=True)

		if draw:
			for con in finalContours:
				x, y, w, h = con[3]
				# cv2.rectangle(img,(x,y),(x+w,y+h), (255,0,0), 3)
				# cv2.polylines(img, con[4], True, (0, 255, 0), 2)
				# cv2.drawContours(img, con[4], -1, (0, 0, 255), 3)

		return img, finalContours


	def reorder(self, points):
		"""
			Reordena las coordenadas de un cuadrado o rectángulo, de forma
			que queden consecutivos leyendo de izquierda a derecha y de
			arriba a abajo.

			points: array, Coordenadas de un cuadrado o rectángulo.
		"""
		newPoints = np.zeros_like(points)
		points = points.reshape((4,2))
		add = points.sum(1)
		newPoints[0] = points[np.argmin(add)]
		newPoints[3] = points[np.argmax(add)]
		diff = np.diff(points, axis=1)
		newPoints[1] = points[np.argmin(diff)]
		newPoints[2] = points[np.argmax(diff)]
		return newPoints