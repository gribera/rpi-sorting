import cv2
import numpy as np
from collections import OrderedDict
import tracker as tracker

class Formas:
	knownObjects = [['Circulo', 'Cuadrado', 'Rectangulo', 'Triangulo', 'Indefinido'], [1, 2, 3, 4, 5]]

	def __init__(self):
		self.tracker = tracker.Tracker()

	def findDis(self, pts1, pts2):
		return (((pts2[0]-pts1[0])**2 + (pts2[1]-pts1[1])**2)**0.5)/28

	def detectShape(self, pts):
		lados = len(pts)
		forma = ''
		if (lados == 3):
			forma = 'Triangulo'
		elif (lados == 4):
			mW = round((self.findDis(pts[0][0], pts[1][0])),1)
			nH = round((self.findDis(pts[0][0], pts[2][0])),1)
			if (mW == nH):
				forma = 'Cuadrado'
			else:
				forma = 'Rectangulo'
		elif (lados > 6):
			forma = 'Circulo'
		else:
			forma = 'Indefinido'

		return forma

	def getContours(self, frame, minArea=1000, returnMask=False):
		"""
			Recupera los contornos de los objetos encontrados utilizando Canny.

			frame: array, Frame.
			minArea: int, Área mínima de los objetos a detectar
			returnMask: boolean, Indica si devuelve el frame o la máscara
		"""
		imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
				if len(poli) == 4:
					poli = self.reorder(poli)
				bbox = cv2.boundingRect(poli)
				txt = self.detectShape(poli)

				finalContours.append([cnt, area, poli, bbox, txt])


		finalContours = sorted(finalContours, key = lambda x: x[1], reverse=True)

		if returnMask:
			return imgThre, finalContours
		else:
			return frame, finalContours

	def getKnownObjects(self):
		"""
			Devuelve los objetos reconocidos por esta clase.
		"""
		return self.knownObjects

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