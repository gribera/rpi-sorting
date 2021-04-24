import cv2
import numpy as np
import tracker as tracker

class Patrones:
	orb = None
	knownObjects = [['Coca-Cola', 'Pepsi', 'Manaos', 'Schweppes', 'Desconocido'], [1, 2, 3, 4, 5]]
	imgPaths =['img_models/coca-cola.png', 'img_models/pepsi.png', 'img_models/manaos.png', 'img_models/schweppes.png']
	images = []

	def __init__(self):
		"""
			Constructor.
		"""
		self.tracker = tracker.Tracker()
		self.orb = cv2.ORB_create(nfeatures=1000)

		for img in self.imgPaths:
			curImg = cv2.imread(img, 0)
			self.images.append(curImg)

	def findDes(self):
		desList = []
		for img in self.images:
			kp, des = self.orb.detectAndCompute(img, None)
			desList.append(des)
		return desList

	def findID(self, img, desList):
		kp2, des2 = self.orb.detectAndCompute(img, None)
		bf = cv2.BFMatcher()
		matchList = []
		finalVal = -1
		try:
			for des in desList:
				matches = bf.knnMatch(des, des2, 2)
				good = []
				for m, n in matches:
					if m.distance < 0.75*n.distance:
						good.append([m])
				matchList.append(len(good))
		except:
			pass

		if len(matchList) != 0:
			if max(matchList) > 10:
				finalVal = matchList.index(max(matchList))

		return finalVal


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
				bbox = cv2.boundingRect(poli)
				x,y,w,h = bbox
				croppedImg = imgGray[y:y+h, x:x+w]
				desList = self.findDes()
				id = self.findID(croppedImg, desList)
				if id > -1:
					txt = self.knownObjects[0][id]
				else:
					txt = 'Objeto desconocido'

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