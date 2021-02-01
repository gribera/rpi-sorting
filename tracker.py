import numpy as np
from collections import OrderedDict
from scipy.spatial import distance as dist
from trackable_object import TrackableObject

class Tracker:
	def __init__(self, maxDisappeared=1, maxDistance=50):
		"""
			Constructor.

			maxDisappeared: int, Tiempo de desaparición del objeto (1 por defecto).
			maxDistance: int, Máxima distancia entre objetos a detectar (50 por defecto).
		"""
		self.initializeTrackableObjects(maxDisappeared, maxDistance)

	def initializeTrackableObjects(self, maxDisappeared, maxDistance):
		"""
			Inicializa los valores del objeto tracker.

			maxDisappeared: int, Tiempo de desaparición del objeto.
			maxDistance: int, Máxima distancia entre objetos a detectar
		"""
		self.nextObjectID = 0
		self.disappeared = OrderedDict()
		self.maxDisappeared = maxDisappeared
		self.maxDistance = maxDistance
		self.trackableObjects = {}

	def setTrackableObjects(self, figs):
		"""
			Setea los objetos detectados.

			figs: array, Array con todos los valores de cada objeto.
		"""

		# check to see if the list of input bounding box rectangles
		# is empty
		if len(figs) == 0:
			# loop over any existing tracked objects and mark them
			# as disappeared
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1

				# if we have reached a maximum number of consecutive
				# frames where a given object has been marked as
				# missing, deregister it
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)

			# return early as there are no centroids or tracking info
			# to update
			return self.trackableObjects

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(figs), 2), dtype="int")

		poli = []
		bbox = []
		# loop over the bounding box rectangles
		[bbox.append(f[3]) for f in figs]
		for (i, (startX, startY, endX, endY)) in enumerate(bbox):
			# use the bounding box coordinates to derive the centroid
			cX = int((startX + (startX+endX)) / 2.0)
			cY = int((startY + (startY+endY)) / 2.0)

			inputCentroids[i] = (cX, cY)

			poli.append(figs[i][2])

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.trackableObjects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(figs[i][0], inputCentroids[i], poli[i], bbox[i], figs[i][4])

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.trackableObjects.keys())
			objectCentroids = []
			[objectCentroids.append(self.trackableObjects[i].centroids[0]) for i in objectIDs]

			# compute the distance between each pair of object
			# centroids and input centroids, respectively -- our
			# goal will be to match an input centroid to an existing
			# object centroid
			D = dist.cdist(np.array(objectCentroids), inputCentroids)

			# in order to perform this matching we must (1) find the
			# smallest value in each row and then (2) sort the row
			# indexes based on their minimum values so that the row
			# with the smallest value as at the *front* of the index
			# list
			rows = D.min(axis=1).argsort()

			# next, we perform a similar process on the columns by
			# finding the smallest value in each column and then
			# sorting using the previously computed row index list
			cols = D.argmin(axis=1)[rows]

			# in order to determine if we need to update, register,
			# or deregister an object we need to keep track of which
			# of the rows and column indexes we have already examined
			usedRows = set()
			usedCols = set()
			# loop over the combination of the (row, column) index
			# tuples

			for (row, col) in zip(rows, cols):
				# if we have already examined either the row or
				# column value before, ignore it
				if row in usedRows or col in usedCols:
					continue

				# if the distance between centroids is greater than
				# the maximum distance, do not associate the two
				# centroids to the same object
				if D[row, col] > self.maxDistance:
					continue

				# otherwise, grab the object ID for the current row,
				# set its new centroid, and reset the disappeared
				# counter
				objectID = objectIDs[row]
				self.disappeared[objectID] = 0

				# Actualiza los bordes y los centros del objeto
				self.trackableObjects[objectID].setContours(figs[col][0])
				self.trackableObjects[objectID].setCentroid(inputCentroids[col])
				self.trackableObjects[objectID].setPoligon(figs[col][2])
				self.trackableObjects[objectID].setBoundingBox(figs[col][3])
				self.trackableObjects[objectID].setText(figs[col][4])

				# indicate that we have examined each of the row and
				# column indexes, respectively
				usedRows.add(row)
				usedCols.add(col)

			# compute both the row and column index we have NOT yet
			# examined
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)

			# in the event that the number of object centroids is
			# equal or greater than the number of input centroids
			# we need to check and see if some of these objects have
			# potentially disappeared
			if D.shape[0] >= D.shape[1]:
				# loop over the unused row indexes
				for row in unusedRows:
					# grab the object ID for the corresponding row
					# index and increment the disappeared counter
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1

					# check to see if the number of consecutive
					# frames the object has been marked "disappeared"
					# for warrants deregistering the object
					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)

			# otherwise, if the number of input centroids is greater
			# than the number of existing object centroids we need to
			# register each new input centroid as a trackable object
			else:
				for col in unusedCols:
					self.register(figs[i][0], inputCentroids[col], poli[i], bbox[i], figs[i][4])

	def register(self, contours, centroid, poli, bbox, txt):
		"""
			Registra el objeto detectado.

			contours: array, Contornos del objeto.
			centroid: array, Array con las coordenadas X, Y del objeto.
			poli: array, Polígono del objeto.
			bbox: array, Rectángulo del objeto.
			txt: string, Texto del objeto.
		"""
		self.disappeared[self.nextObjectID] = 0
		to = TrackableObject(self.nextObjectID, contours, centroid, poli, bbox, txt)
		self.trackableObjects[self.nextObjectID] = to
		self.nextObjectID += 1

	def deregister(self, objectID):
		del self.disappeared[objectID]
		del self.trackableObjects[objectID]

	def getTrackableObjects(self):
		return self.trackableObjects
