import cv2
import numpy as np
from collections import OrderedDict
from scipy.spatial import distance as dist
from trackable_object import TrackableObject

class Colores:
	blue_lower = np.array([100,100,23], np.uint8)
	blue_upper = np.array([125,255,255], np.uint8)

	yellow_lower = np.array([15,100,20], np.uint8)
	yellow_upper = np.array([45,255,255], np.uint8)

	red1_lower = np.array([0,100,20], np.uint8)
	red1_upper = np.array([5,255,255], np.uint8)

	red2_lower = np.array([175,100,20], np.uint8)
	red2_upper = np.array([179,255,255], np.uint8)

	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)

	colores = ['blue', 'yellow', 'red']
	masks = [0, 0, 0]
	total = [0, 0, 0]

	trackableObjects = {}
	rects = []
	border_colors = [(255,0,0), (0,255,0), (0,0,255)]

	def __init__(self, maxDisappeared=50, maxDistance=50):
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.maxDisappeared = maxDisappeared
		self.maxDistance = maxDistance

		self.cap = cv2.VideoCapture(0)
		self.frame = None


	def start(self):
		while True:
			ret, self.frame = self.cap.read()

			self.rects = []
			frameHSV = self.setHSVColorModel()
			self.maskFrame(frameHSV)
			self.dibujarContornos((255,0,0))
			self.update(self.rects)
			self.setTrackeableObjects()

			# construct a tuple of information we will be displaying on the
			# frame
			info = [
				("TrackableObjs", 0),
				("Down", self.total),
				("Status", 10),
			]

			for i in range(len(self.colores)):
				text = "{}: {}".format(self.colores[i], self.total[i])
				cv2.putText(self.frame, text, (10, ((i * 20) + 20)),
					cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

			# loop over the info tuples and draw them on our frame
			# for (i, (k, v)) in enumerate(info):
			# 	text = "{}: {}".format(k, v)
			# 	cv2.putText(self.frame, text, (10, ((i * 20) + 20)),
			# 		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

			if ret == True:
				cv2.imshow('Frame', self.frame)

			if cv2.waitKey(1) & 0xFF == ord('s'):
				break

		self.destroy()

	def setHSVColorModel(self):
		return cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	def maskFrame(self, frameHSV):
		self.masks[0] = cv2.inRange(frameHSV, self.blue_lower, self.blue_upper)
		self.masks[1] = cv2.inRange(frameHSV, self.yellow_lower, self.yellow_upper)
		self.masks[2] = cv2.add(
				cv2.inRange(frameHSV, self.red1_lower, self.red1_upper),
				cv2.inRange(frameHSV, self.red2_lower, self.red2_upper)
			)

	def dibujarContornos(self, color):
		for mask in range(len(self.masks)):
			(contornos,hierarchy) = cv2.findContours(self.masks[mask], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			for pic, contour in enumerate(contornos):
				if (cv2.contourArea(contour) > 600):
					x,y,w,h = cv2.boundingRect(contour)
					cv2.rectangle(self.frame,(x,y),(x+w,y+h),color, 3)
					cv2.putText(self.frame, '{},{}'.format(x, y), (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [255,255,0], 1, cv2.LINE_AA)

					M = cv2.moments(contour)
					fx = int(M["m10"] / M["m00"])
					fy = int(M["m01"] / M["m00"])
					self.dibujarPunto(fx, fy)
					self.rects.append((mask, x, y, w, h))

	def setTrackeableObjects(self):
		for (objectID, centroid) in self.objects.items():
			# check to see if a trackable object exists for the current
			# object ID
			to = self.trackableObjects.get(objectID, None)

			# if there is no existing trackable object, create one
			if to is None:
				print('Asigno color')
				to = TrackableObject(objectID, centroid)
				print(to.color)
				# print(self.color[to.color])

			if not to.counted:
				self.total[to.color] += 1
				to.counted = True

			# store the trackable object in our dictionary
			self.trackableObjects[objectID] = to

			# draw both the ID of the object and the centroid of the
			# object on the output frame
			text = "ID {}".format(objectID)
			cv2.putText(self.frame, text, (centroid[0] - 10, centroid[1] - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			cv2.circle(self.frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


	def dibujarLinea(self):
		cv2.line(self.frame, (0 , 230), (640 , 230), (100,155,30), 3)

	def dibujarPunto(self, x, y):
		cv2.circle(self.frame, (x,y), 7, (0, 255, 0), -1)

	def update(self, rects):
		# check to see if the list of input bounding box rectangles
		# is empty
		if len(rects) == 0:
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
			return self.objects

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(rects), 3), dtype="int")

		# loop over the bounding box rectangles
		for (i, (color, startX, startY, endX, endY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (color, cX, cY)

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

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
				self.objects[objectID] = inputCentroids[col]
				self.disappeared[objectID] = 0

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
					self.register(inputCentroids[col])

		return self.objects

	def register(self, centroid):
		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1

	def deregister(self, objectID):
		del self.objects[objectID]
		del self.disappeared[objectID]

	def destroy(self):
		self.cap.release()
		cv2.destroyAllWindows()
