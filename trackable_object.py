class TrackableObject:
	def __init__(self, objectID, centroid, poli, bbox, txt):
		self.objectID = objectID
		self.centroids = [centroid]
		self.poli = poli
		self.bbox = bbox
		self.text = txt
		self.classified = False
		self.counted = False

	def getCentroidX(self):
		return self.centroids[0][0]

	def getCentroidY(self):
		return self.centroids[0][1]

	def getTxt(self):
		return self.text

	def isClassified(self):
		return self.classified

	def setCentroid(self, centroid):
		self.centroids = [centroid]

	def setPoligon(self, poli):
		self.poli = poli

	def setBoundingBox(self, bbox):
		self.bbox = bbox

	def setText(self, text):
		self.text = text

	def setMedida(self, medida):
		self.medida = medida

	def setClassified(self):
		self.classified = True

	def setCounted(self):
		self.counted = True
