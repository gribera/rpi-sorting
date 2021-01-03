class TrackableObject:
	def __init__(self, objectID, contours, centroid, poli, bbox, txt):
		"""
			Constructor.

			objectID: int, ID del objeto detectado.
			contours: array, Contornos del objeto.
			centroid: array, Coordenadas X, Y del centro del objeto.
			poli: array, Bordes del objeto.
			bbox: array, Rectángulo del objeto.
			txt: string, Texto del objeto.
		"""
		self.objectID = objectID
		self.contours = contours
		self.centroids = [centroid]
		self.poli = poli
		self.bbox = bbox
		self.text = txt
		self.classified = False
		self.counted = False

	def getCentroidX(self):
		"""
			Devuelve coordenada X del objeto.
		"""
		return self.centroids[0][0]

	def getCentroidY(self):
		"""
			Devuelve coordenada Y del objeto.
		"""
		return self.centroids[0][1]

	def getContours(self):
		"""
			Devuelve contornos del objeto.
		"""
		return self.contours

	def getTxt(self):
		"""
			Devuelve texto del objeto.
		"""
		return self.text

	def isClassified(self):
		"""
			Devuelve True o False en caso de que el objeto haya sido clasificado o no.
		"""
		return self.classified

	def setCentroid(self, centroid):
		"""
			Setea coordenadas del centro del objeto.
		"""
		self.centroids = [centroid]

	def setPoligon(self, poli):
		"""
			Setea bordes del objeto.
		"""
		self.poli = poli

	def setBoundingBox(self, bbox):
		"""
			Setea rectángulo del objeto.
		"""
		self.bbox = bbox

	def setContours(self, contours):
		"""
			Setea contornos del objeto.
		"""
		self.contours = contours

	def setText(self, text):
		"""
			Setea texto del objeto.
		"""
		self.text = text

	def setMedida(self, medida):
		"""
			Setea medida del objeto (sólo en modalidad 'forma').
		"""
		self.medida = medida

	def setClassified(self):
		"""
			Setea si el objeto fué clasificado.
		"""
		self.classified = True

	def setCounted(self):
		"""
			Setea si el objeto fué contado (sólo en modalidad 'color').
		"""
		self.counted = True
