import cv2
import numpy as np
import vision as vision
import colores as colores
import formas as formas
import tracker as tracker

class Manager:
	vision = vision.Vision()
	trackableObjects = {}

	def __init__(self, modalidad):
		if modalidad == 'color':
			self.color = colores.Colores()
		if modalidad == 'forma':
			self.forma = formas.Formas()

		self.modalidad = modalidad
		self.tracker = tracker.Tracker()

	def start(self):
		while True:
			self.vision.readFrame()
			self.vision.rotateImage()
			self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
			self.frame = self.vision.getFrame()

			imgContours, finalContours = self.getContours()

			if len(finalContours) != 0:
				self.tracker.setTrackableObjects(finalContours)

				self.trackableObjects = self.tracker.getTrackableObjects()

				self.showInfo(imgContours)

			self.vision.showFrame(imgContours)

			if self.vision.waitForKey('s'):
				break

		self.vision.destroy()

	def getFrame(self):
		self.vision.readFrame()
		self.vision.rotateImage()
		self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
		self.frame = self.vision.getFrame()

		imgContours, finalContours = self.getContours()

		if len(finalContours) != 0:
			self.tracker.setTrackableObjects(finalContours)

			self.trackableObjects = self.tracker.getTrackableObjects()

			self.showInfo(imgContours)

		return self.vision.getStringData(imgContours)

	def getContours(self):
		if self.modalidad == 'forma':
			imgContours, finalContours = self.forma.getContours(self.frame, minArea=1000)
		if self.modalidad == 'color':
			imgContours, finalContours = self.color.getContours(self.frame, minArea=1000)

		return imgContours, finalContours

	def showInfo(self, imgContours):
		if self.modalidad == 'forma':
			self.printFormaInfo(imgContours, self.trackableObjects, showID=True, showForma=True,
							  showCentroid=True, position="center", drawContours=True,
							  showBoundingRect=False, measure=True)
		if self.modalidad == 'color':
			self.printColorInfo(imgContours, self.trackableObjects, position="right", showCentroid=True,
								showBoundingRect=True, countItems=True)

	def printColorInfo(self, frame, to, position="center", showCentroid=False, showBoundingRect=False,
					   countItems=False, showID=True):

		if position == "right":
			xDes = 100
		else:
			xDes = 20

		for key, value in to.items():
			x = value.getCentroidX()
			y = value.getCentroidY()
			(startX, startY, w, h) = value.bbox
			if showCentroid == True:
				self.vision.dibujarPunto(x, y)
			if showBoundingRect == True:
				cv2.rectangle(frame,(startX,startY),(startX+w,startY+h),
					self.color.border_colors[value.color], 3)
			if showID:
				text = "ID {}".format(value.objectID)
				cv2.putText(frame, text, (x + xDes, y),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
			if countItems == True:
				if value.counted == False:
					self.color.total[value.color] += 1
					value.setCounted()

				for i in range(len(self.color.colores)):
					text = "{}: {}".format(self.color.colores[i], self.color.total[i])
					cv2.putText(frame, text, (10, ((i * 20) + 20)),
						cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	def printFormaInfo(self, frame, to, position="center", showCentroid=False, showForma=False,
					 showID=False, showBoundingRect=False, drawContours=False, measure=False):
		if position == "center":
			xDes = 20
		if position == "right":
			xDes = 100

		for key, obj in to.items():
			x = obj.getCentroidX()
			y = obj.getCentroidY()
			(startX, startY, w, h) = obj.bbox
			forma = self.forma.detectShape(obj.poli)
			yDes = 0
			if showCentroid == True:
				self.vision.dibujarPunto(x, y)
			if showBoundingRect == True:
				cv2.rectangle(frame,(startX,startY),(startX+w,startY+h), (255,0,0), 3)
			if showID == True:
				text = "ID {}".format(obj.objectID)
				cv2.putText(frame, text, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if showForma == True:
				cv2.putText(frame, forma, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if measure == True:
				if (forma == 'Cuadrado') | (forma == 'Rectangulo'):
					mW = round((self.forma.findDis(obj.poli[0][0], obj.poli[1][0])),1)
					nH = round((self.forma.findDis(obj.poli[0][0], obj.poli[2][0])),1)

					cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
						(obj.poli[1][0][0], obj.poli[1][0][1]), (255,0,255), 2)
					cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
						(obj.poli[2][0][0], obj.poli[2][0][1]), (255,0,255), 2)

					cv2.putText(frame, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7,
						(255,0,255), 2)
					cv2.putText(frame, '{}cm'.format(nH), (startX-70,startY+h//2), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)
