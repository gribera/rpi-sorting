import cv2
import numpy as np

class Vision:
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.frame = None
		self.ret = None

	def readFrame(self):
		"""
			Lee el frame
		"""
		self.ret, self.frame = self.cap.read()
		return

	def getFrame(self):
		""" Devuelve el frame actual """
		return self.frame


	def showFrame(self, frame):
		"""
			Muestra el frame
		"""
		if self.ret == True:
			cv2.imshow('Orig', frame)
		return

	def waitForKey(self, key):
		"""
			Devuelve True si la tecla enviada como parámetro fué presionada
		"""
		return cv2.waitKey(1) & 0xFF == ord(key)

	def getStringData(self, frame):
		"""
			Devuelve un string del buffer pasado por parámetro capturado
		"""
		imgEncode = cv2.imencode('.jpg', frame)[1]
		return imgEncode.tostring()

	def rotateImage(self):
		"""
			Rota la imágen 90 grados
		"""
		self.frame = cv2.flip(self.frame, cv2.ROTATE_90_CLOCKWISE)

	def cutBorders(self, p1, p2, p3, p4, verb):
		"""
			Corta los bordes del frame, eliminando bordes innecesarios

			p1: array, Coordenada x, y del punto 1
			p2: array, Coordenada x, y del punto 2
			p3: array, Coordenada x, y del punto 3
			p4: array, Coordenada x, y del punto 4
			verb: boolean, Muestra los puntos a cortar sobre la imágen
						   sin efectuar el corte
		"""
		if verb:
			self.dibujarPunto(p1[0], p1[1]);
			self.dibujarPunto(p2[0], p2[1]);
			self.dibujarPunto(p3[0], p3[1]);
			self.dibujarPunto(p4[0], p4[1]);
		else:
			pts1 = np.float32([p1, p2, p3, p4])
			pts2 = np.float32([[0,0], [640, 0], [0,480],[640,480]])
			matrix = cv2.getPerspectiveTransform(pts1, pts2)
			self.frame = cv2.warpPerspective(self.frame, matrix, (640, 480))

	def dibujarLinea(self):
		"""
			Dibuja una línea en el centro de la pantalla
		"""
		cv2.line(self.frame, (0 , 230), (640 , 230), (100,155,30), 3)

	def dibujarPunto(self, x, y):
		"""
			Dibuja un punto en las coordenadas especificadas
			x: int, Coordenada X
			y: int, Coordenada Y
		"""
		cv2.circle(self.frame, (x,y), 7, (0, 255, 0), -1)

	def destroy(self):
		self.cap.release()
		cv2.destroyAllWindows()
