# Location Objects for preprocessing model data
from shapely.geometry import LineString, LinearRing, Point, MultiPoint, Polygon
import pyproj
import re

def formatCoordinateString(points):
	""" Format: lat,lng lat,lng ... 
		Points as a list of points [(x, y), (x, y), ...]
	"""
	return " ".join(map(lambda x: str(x[0]) + "," + str(x[1]), points))

def parseCoordinateString(coords_str):
	""" Parse coordinates from string with format: lat,lng lat,lng ...
		Return list of points [(x, y), (x, y), ...]
	"""
	coords = []
	double_re = "[-+]?\d+\.\d+"
	
	# Find all: lat,lng in coordinates string
	coords_re_str = re.findall(double_re + "," + double_re, \
		coords_str)

	# Go through matches, split, and parse
	for crds in coords_re_str:
		coords_vals = crds.rsplit(',')
		lat = float(coords_vals[0])
		lng = float(coords_vals[1])
		coords.append((lat, lng))
	return coords

class Parcel:
	def __init__(self, pid, owner, p_type, address="", distance_to_trail=5000, permissions="", notes=""):
		self.id = pid
		self.points = []
		self.owner = owner
		self.linearRing = None
		self.p_type = p_type
		self.address = address
		self.on_trail = False
		self.distance_to_trail = float("inf")
		self.permissions = permissions
		self.notes = notes

	def convertCoords(self, points):
		c = 0.3048                              #Meters to Feet ratio
		p1 = pyproj.Proj(init='epsg:2925')
		return [p1(point[0]*c, point[1]*c, inverse=True)[::-1] for point in points]

	def addPoints(self, points, coordType):
		self.points = points if coordType == 0 else self.convertCoords(points)
		self.linearRing = LinearRing(self.points)

	def getSize(self):
		""" Return the size in unknown units """
		return Polygon(self.points).area

	def formatCoordinates(self):
		""" Format: lat,long lat,long ... """
		return formatCoordinateString(self.points)

	def __str__(self):
		return "Owner: " + str(self.owner)

	# def __repr__(self):
	# 	return "Owner: " + str(self.owner) + "\nPoints: " + str(self.linearRing)

class Coordinate:
	""" Representation of a Lat,Long,Elev coordinate """
	def __init__(self, lat, lng, elev):
		""" Constructor """
		self.latitude = lat
		self.longitude = lng
		self.elevation = elev

	def getCoords(self):
		return (self.latitude, self.longitude)

	def getOutputCoords(self):
		""" Output long, lat, elevation. Purposefully in this order """
		return (self.longitude, self.latitude, self.elevation)

class LineSegment:
	""" Representation of a LineSegment of coordinates """
	def __init__(self):
		""" Constructor """
		self.coordinates = []

	def getLineString(self):
		return LineString([x.getCoords() for x in self.coordinates])

	def getOutputLineString(self):
		""" Includes elevation in output format """
		return LineString([x.getOutputCoords() for x in self.coordinates])

	def getLines(self):
		coords = self.coordinates
		return [
		LineString([coords[ind].getCoords(), coords[ind+1].getCoords()]) 
			for ind in range(len(coords)-1)
		]

class Atom:
	def __init__(self, linestring, placemark):
		self.placemark = placemark
		self.coordinates = linestring  #shapely LineString
		self.parcel = None

	def setParcel(self, parcel):
		if self.parcel is not None:
			if Polygon(parcel.points).area < Polygon(self.parcel.points).area:
				return
		self.parcel = parcel

	def inParcel(self, parcel):
		midpoint = self.coordinates.centroid
		shape = Polygon(parcel.points)
		return shape.contains(midpoint)

	def formatCoordinates(self):
		""" Format: lat,long lat,long ... """
		return formatCoordinateString([self.coordinates.coords[0], self.coordinates.coords[1]])

	def parseCoordinates(self, coords_str):
		""" Parse coords_str to set coordinates LineString 
			Format: lat,long lat,long ...
		"""
		self.coordinates = LineString(parseCoordinateString(coords_str))

	def setIds(self, segment_id, segment_position_id):
		""" Set id information for which segment and position in segment
		"""
		self.segment = segment_id
		self.position = segment_position_id

class Placemark:
	""" Representation of a Placemark """
	def __init__(self, name, description, status=None, current_conditions=None, styleUrl=None, pk=None):
		""" Constructor """
		self.name = name
		self.description = description
		self.line_segments = []
		self.atoms = []
		self.status = status
		self.current_conditions = current_conditions
		self.styleUrl = styleUrl
		self.id = pk

	def generateAtoms(self, segments):
		for segment_id, s in enumerate(segments):
			current_pos = 0
			for line in s:
				for l in line.getLines():
					atom = Atom(l, self)
					atom.setIds(segment_id, current_pos)
					self.atoms.append(atom)
					current_pos += 1