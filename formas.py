import cv2
import numpy as np
from collections import OrderedDict
import vision as vision
import tracker as tracker

class Formas:
	vision = vision.Vision()

	def __init__(self):
		self.tracker = tracker.Tracker()

	def start(self):
		while True:
			self.vision.readFrame()
			self.vision.rotateImage()
			self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
			frame = self.vision.getFrame()

			imgContours, finalContours = self.getContours(frame, minArea=1000)

			if len(finalContours) != 0:
				self.tracker.setTrackableObjects(finalContours)

				trackableObjects = self.tracker.getTrackableObjects()
				self.printObjInfo(imgContours, trackableObjects, showID=True, showForma=True,
								  showCentroid=True, position="center", drawContours=True,
								  showBoundingRect=False, measure=True)

			self.vision.showFrame(imgContours)

			if self.vision.waitForKey('s'):
				break

		self.vision.destroy()

	def findDis(self, pts1, pts2):
		"""
			Busca la distancia entre dos puntos.

			img: array, Frame.
			minArea: int, Área mínima de los objetos a detectar
			filter: int, Filtro de cantidad de bordes (detecta contornos con la
													   cantidad de bordes especificada)
			draw: bool, Muestra los bordes
		"""
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

	def printObjInfo(self, img, to, position="center", showCentroid=False, showForma=False,
					 showID=False, showBoundingRect=False, drawContours=False, measure=False):
		if position == "center":
			xDes = 20
		if position == "right":
			xDes = 100

		for key, value in to.items():
			x = value.getCentroidX()
			y = value.getCentroidY()
			(startX, startY, w, h) = value.bbox
			yDes = 0
			if showCentroid == True:
				self.vision.dibujarPunto(x, y)
			if showBoundingRect == True:
				cv2.rectangle(img,(startX,startY),(startX+w,startY+h), (255,0,0), 3)
			# if drawContours == True:
			# 	cv2.drawContours(img, value.poli, 0, (0, 255, 0), 2)
			if showID == True:
				text = "ID {}".format(value.objectID)
				cv2.putText(img, text, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if showForma == True:
				text = self.detectShape(len(value.poli))
				cv2.putText(img, text, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if measure == True:
				if self.detectShape(len(value.poli)) == 'Cuadrado':
					nPoints = self.reorder(value.poli)
					mW = round((self.findDis(nPoints[0][0], nPoints[1][0])),1)
					nH = round((self.findDis(nPoints[0][0], nPoints[2][0])),1)

					cv2.arrowedLine(img, (nPoints[0][0][0],nPoints[0][0][1]), (nPoints[1][0][0], nPoints[1][0][1]), (255,0,255), 2)
					cv2.arrowedLine(img, (nPoints[0][0][0],nPoints[0][0][1]), (nPoints[2][0][0], nPoints[2][0][1]), (255,0,255), 2)
					# x, y, w, h = obj[3]
					cv2.putText(img, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)
					cv2.putText(img, '{}cm'.format(nH), (startX-70,startY+h//2), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)


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
						finalContours.append([cnt, area, poli, bbox])
				else:
					finalContours.append([cnt, area, poli, bbox])

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


	# def warpImg(self, img, points, w, h):
	# 	pts1 = np.float32(self.reorder(points))
	# 	pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
	# 	matrix = cv2.getPerspectiveTransform(pts1, pts2)
	# 	imgWarp = cv2.warpPerspective(img, matrix, (w,h))
	# 	return imgWarp