import cv2
import numpy as np
import vision as vision
import colores as colores
import formas as formas
import codigos as codigos
import tracker as tracker
import cinta as cinta
import classifier as classifier

class Manager:
	vision = vision.Vision()
	trackableObjects = {}
	params = {}
	object = None
	infoFunction = None
	knownObjects = None

	def __init__(self, modalidad):
		"""
			Constructor.

			modalidad: string, Modo de trabajo [color, forma, codigo]
		"""
		self.cinta = cinta.Cinta()
		self.classifier = classifier.Classifier()
		self.tracker = tracker.Tracker()
		self.modalidad = modalidad
		self.iniciarObjeto()

		# Parámetros por defecto de las vistas
		dicParams = {
			'showID': False,
			'showTxt': False,
			'showCentroid': False,
			'showBoundingRect': False,
			'showMask': False,
			'position': 'center',
			'drawContours': False,
			'measure': False,
			'countItems': False,
			'classify': False
		}

		self.setVariables(dicParams)

	def setVariables(self, dicParams):
		"""
			Actualiza el diccionario con los parámetros

			dicParams: dict, Diccionario de parámetros
		"""
		self.params = dicParams

	def iniciarObjeto(self):
		"""
			Inicializa objeto de acuerdo a la modalidad de trackeo
		"""
		if self.object:
			del self.object

		if self.modalidad == 'color':
			self.object = colores.Colores()
			self.infoFunction = self.printColorInfo
		if self.modalidad == 'forma':
			self.object = formas.Formas()
			self.infoFunction = self.printFormaInfo
		if self.modalidad == 'codigo':
			self.object = codigos.Codigos()
			self.infoFunction = self.printCodigoInfo

		self.knownObjects = self.object.getKnownObjects()

		if self.tracker:
			del self.tracker
			self.tracker = tracker.Tracker()

	def getFrame(self):
		"""
			Lee el frame, hace un tratamiento a la imágen y detecta los objetos
		"""
		self.vision.readFrame()
		self.vision.rotateImage()
		self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
		self.frame = self.vision.getFrame()

		imgContours, finalContours = self.getContours()

		if len(finalContours) != 0:
			self.tracker.setTrackableObjects(finalContours)

			self.trackableObjects = self.tracker.getTrackableObjects()

			for key, obj in self.trackableObjects.items():
				self.showInfo(imgContours, obj)
				if not obj.isClassified():
					self.classify(obj)

		return self.vision.getStringData(imgContours)

	def cambioModo(self, modo):
		"""
			Cambia modo de trabajo

			modo: string, Modo de trabajo [color, forma, codigo]
		"""
		self.modalidad = modo
		self.iniciarObjeto()

	def getContours(self):
		imgContours, finalContours = self.object.getContours(self.frame, returnMask=self.params['showMask'])

		return imgContours, finalContours

	def classify(self, obj):
		try:
			index = self.knownObjects[0].index(obj.getTxt())
			target = self.knownObjects[1][index]
			self.classifier.classify(target)
			obj.setClassified()
		except ValueError:
			pass

	def getPosition(self, align, xDes, yDes):
		"""
			Devuelve la posición x, y de acuerdo a la alineación pasada por parámetro

			align: string, Alineación [center, right]
			xDes: int, Coordenada x
			yDes: int, Coordenada y
		"""
		if align == "center":
			xDes = xDes + 20
		if align == "right":
			xDes = xDes + 100

		yDes += 15

		return xDes, yDes

	def showInfo(self, frame, obj):
		"""
			Agrega al frame la información del objeto que se haya seteado para mostrar.

			frame: array, Frame
			obj: TrackableObject, Objeto detectado
		"""
		x = obj.getCentroidX()
		y = obj.getCentroidY()
		if self.params['showCentroid'] == True:
			self.vision.dibujarPunto(x, y)
		if self.params['showBoundingRect'] == True:
			(startX, startY, w, h) = obj.bbox
			cv2.rectangle(frame,(startX,startY),(startX+w,startY+h), (255,0,0), 3)
		if self.params['drawContours'] == True:
			cv2.drawContours(frame, obj.getContours(), -1, [0, 255, 0], 3)
		if self.params['showID']:
			posX, posY = self.getPosition(self.params['position'], x, y)
			text = "ID {}".format(obj.objectID)
			cv2.putText(frame, text, (posX, posY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
		if self.params['showTxt'] == True:
			posX, posY = self.getPosition(self.params['position'], x, y + 15)
			cv2.putText(frame, obj.getTxt(), (posX, posY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)

		self.infoFunction(frame, obj)

	def printColorInfo(self, frame, obj):
		"""
			Agrega al frame información particular sobre el color.

			frame: array, Frame
			obj: TrackableObject, Objeto detectado
		"""
		if self.params['countItems'] == True:
			if obj.counted == False:
				self.object.total[obj.color] += 1
				obj.setCounted()

			for i in range(len(self.object.colores)):
				text = "{}: {}".format(self.object.colores[i], self.object.total[i])
				cv2.putText(frame, text, (10, ((i * 20) + 20)),
					cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	def printFormaInfo(self, frame, obj):
		"""
			Agrega al frame información particular sobre la forma.

			frame: array, Frame
			obj: TrackableObject, Objeto detectado
		"""
		x = obj.getCentroidX()
		y = obj.getCentroidY()
		(startX, startY, w, h) = obj.bbox
		forma = obj.getTxt()
		if self.params['measure'] == True:
			if (forma == 'Cuadrado') | (forma == 'Rectangulo'):
				mW = round((self.object.findDis(obj.poli[0][0], obj.poli[1][0])), 1)
				nH = round((self.object.findDis(obj.poli[0][0], obj.poli[2][0])), 1)

				cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
					(obj.poli[1][0][0], obj.poli[1][0][1]), (255,0,255), 2)
				cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
					(obj.poli[2][0][0], obj.poli[2][0][1]), (255,0,255), 2)

				cv2.putText(frame, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7,
					(255,0,255), 2)
				cv2.putText(frame, '{}cm'.format(nH), (startX-70,startY+h//2), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)
			if forma == 'Circulo':
				border = obj.getContours()[0][0]
				mW = round((self.object.findDis([x, y], [border[0], border[1]])), 1)
				cv2.arrowedLine(frame, (x, y), (border[0], border[1]), (255,0,255), 2)
				cv2.putText(frame, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7,
					(255,0,255), 2)

	def printCodigoInfo(self, frame, obj):
		"""
			Agrega al frame información particular sobre el código.

			frame: array, Frame
			obj: TrackableObject, Objeto detectado
		"""
		pass

	def moverCinta(self, velocidad):
		"""
			Inicia elmovimiento de la cinta.

			velocidad: int, Velocidad (Valor de 0 al 6)
		"""
		self.cinta.setVelocidad(velocidad)

	def cambiarDireccionCinta(self):
		"""
			Cambia la dirección de la cinta.
		"""
		self.cinta.setDireccion()

	def toggleShowID(self):
		"""
			Muestra u oculta ID.
		"""
		self.params['showID'] = not self.params['showID']

	def toggleShowCentroid(self):
		"""
			Muestra u oculta centro del objeto.
		"""
		self.params['showCentroid'] = not self.params['showCentroid']

	def toggleDrawContours(self):
		"""
			Muestra u oculta contornos del objeto.
		"""
		self.params['drawContours'] = not self.params['drawContours']

	def toggleShowTxt(self):
		"""
			Muestra u oculta texto del objeto.
		"""
		self.params['showTxt'] = not self.params['showTxt']

	def toggleShowBoundingRect(self):
		"""
			Muestra u oculta rectángulo del objeto.
		"""
		self.params['showBoundingRect'] = not self.params['showBoundingRect']

	def toggleShowMeasure(self):
		"""
			Muestra u oculta medida del objeto (sólo en modalidad 'forma').
		"""
		self.params['measure'] = not self.params['measure']

	def toggleShowMask(self):
		"""
			Muestra frame o máscara.
		"""
		self.params['showMask'] = not self.params['showMask']

	def getColorRanges(self):
		"""
			Recupera rangos de colores (sólo en modalidad 'color').
		"""
		return self.object.getColorRanges()

	def setColorRanges(self, colores):
		"""
			Setea rangos de colores (sólo en modalidad 'color').
		"""
		return self.objeto.setColorRanges(colores)