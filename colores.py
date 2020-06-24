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
		self.cap = cv2.VideoCapture(0)
		self.frame = None
		self.tracker = tracker.Tracker()

	def start(self):
		while True:
			ret, self.frame = self.cap.read()
			self.frame = cv2.flip(self.frame, cv2.ROTATE_90_CLOCKWISE) # Rota la imagen 90 degrees

			self.rects = []
			frameHSV = self.setHSVColorModel()
			self.maskFrame(frameHSV)
			self.dibujarContornos()
			self.tracker.update(self.rects)
			self.total = self.tracker.setTrackeableObjects(self.total)
			self.markObjects()
			self.showResults()

			if ret == True:
				cv2.imshow('Frame', self.frame)

			if cv2.waitKey(1) & 0xFF == ord('s'):
				break

		self.destroy()

	def markObjects(self):
		for (objectID, coords) in self.tracker.getObjects():
			text = "ID {}".format(objectID)
			cv2.putText(self.frame, text, (coords[1] + 10, coords[2]),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			self.dibujarPunto(coords[1], coords[2])

	def showResults(self):
		for i in range(len(self.colores)):
			text = "{}: {}".format(self.colores[i], self.total[i])
			cv2.putText(self.frame, text, (10, ((i * 20) + 20)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	def setHSVColorModel(self):
		return cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	def maskFrame(self, frameHSV):
		self.masks[0] = cv2.inRange(frameHSV, self.blue_lower, self.blue_upper)
		self.masks[1] = cv2.inRange(frameHSV, self.yellow_lower, self.yellow_upper)
		self.masks[2] = cv2.add(
				cv2.inRange(frameHSV, self.red1_lower, self.red1_upper),
				cv2.inRange(frameHSV, self.red2_lower, self.red2_upper)
			)

	def dibujarContornos(self):
		for mask in range(len(self.masks)):
			(_,contornos,hierarchy) = cv2.findContours(self.masks[mask], cv2.RETR_EXTERNAL, 
				cv2.CHAIN_APPROX_SIMPLE)
			for pic, contour in enumerate(contornos):
				if (cv2.contourArea(contour) > 600):
					x,y,w,h = cv2.boundingRect(contour)
					cv2.rectangle(self.frame,(x,y),(x+w,y+h), self.border_colors[mask], 3)
					cv2.putText(self.frame, '{},{}'.format(x, y), (x+10, y), 
						cv2.FONT_HERSHEY_SIMPLEX, 0.75, [255,255,0], 1, cv2.LINE_AA)
					self.rects.append((mask, x, y, w, h))

	def dibujarLinea(self):
		cv2.line(self.frame, (0 , 230), (640 , 230), (100,155,30), 3)

	def dibujarPunto(self, x, y):
		cv2.circle(self.frame, (x,y), 7, (0, 255, 0), -1)

	def destroy(self):
		self.cap.release()
		cv2.destroyAllWindows()
