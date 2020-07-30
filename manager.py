import cv2
import numpy as np
import vision as vision
import colores as colores
import formas as formas
import tracker as tracker

class Manager:
	trackableObjects = {}
	vision = vision.Vision()
	color = colores.Colores()
	forma = formas.Formas()

	def __init__(self):
		self.tracker = tracker.Tracker()

	def start(self, modalidad):
		while True:
			self.vision.readFrame()
			self.vision.rotateImage()
			self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
			frame = self.vision.getFrame()

			imgContours, finalContours = self.getContours(frame, modalidad)

			if len(finalContours) != 0:
				self.tracker.setTrackableObjects(finalContours)

				self.trackableObjects = self.tracker.getTrackableObjects()

				self.showInfo(imgContours, modalidad)

			self.vision.showFrame(imgContours)

			if self.vision.waitForKey('s'):
				break

		self.vision.destroy()

	def getContours(self, frame, modalidad):
		if modalidad == 'forma':
			imgContours, finalContours = self.forma.getContours(frame, minArea=1000)
		if modalidad == 'color':
			imgContours, finalContours = self.color.getContours(frame, minArea=1000)

		return imgContours, finalContours

	def showInfo(self, imgContours, modalidad):
		if modalidad == 'forma':
			self.printFormaInfo(imgContours, self.trackableObjects, showID=True, showForma=True,
							  showCentroid=True, position="center", drawContours=True,
							  showBoundingRect=False, measure=True)
		if modalidad == 'color':
			self.printColorInfo(imgContours, self.trackableObjects, position="right", showCentroid=True,
								showBoundingRect=True, countItems=True)

	def printColorInfo(self, img, to, position="center", showCentroid=False, showBoundingRect=False,
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
				cv2.rectangle(img,(startX,startY),(startX+w,startY+h),
					self.color.border_colors[value.color], 3)
			if showID:
				text = "ID {}".format(value.objectID)
				cv2.putText(img, text, (x + xDes, y),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
			if countItems == True:
				if value.counted == False:
					self.color.total[value.color] += 1
					value.setCounted()

				for i in range(len(self.color.colores)):
					text = "{}: {}".format(self.color.colores[i], self.color.total[i])
					cv2.putText(img, text, (10, ((i * 20) + 20)),
						cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	def printFormaInfo(self, img, to, position="center", showCentroid=False, showForma=False,
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
			if showID == True:
				text = "ID {}".format(value.objectID)
				cv2.putText(img, text, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if showForma == True:
				text = self.forma.detectShape(len(value.poli))
				cv2.putText(img, text, (x + xDes, y + yDes),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
				yDes += 15
			if measure == True:
				if self.forma.detectShape(len(value.poli)) == 'Cuadrado':
					nPoints = self.forma.reorder(value.poli)
					mW = round((self.forma.findDis(nPoints[0][0], nPoints[1][0])),1)
					nH = round((self.forma.findDis(nPoints[0][0], nPoints[2][0])),1)

					cv2.arrowedLine(img, (nPoints[0][0][0],nPoints[0][0][1]), (nPoints[1][0][0], nPoints[1][0][1]), (255,0,255), 2)
					cv2.arrowedLine(img, (nPoints[0][0][0],nPoints[0][0][1]), (nPoints[2][0][0], nPoints[2][0][1]), (255,0,255), 2)
					# x, y, w, h = obj[3]
					cv2.putText(img, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)
					cv2.putText(img, '{}cm'.format(nH), (startX-70,startY+h//2), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)
