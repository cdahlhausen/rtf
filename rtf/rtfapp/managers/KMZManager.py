# Manager system for interacting with KMZ (zipped KML dirs) files
from . import FileSystemManager
from fastkml import kml
import xml.etree.ElementTree as ET
import re
from rtfapp.managers.LocationObjects import Placemark, Coordinate, LineSegment
from shapely.geometry import MultiLineString

CLOSED_COLOR = "FF0000"

def extractKMLFiles(kmzPath, kmzDir=None):
	""" Extract zipped KML files from specified path and return 
		absolute file path to list of KML files """
	filelist = []

	if (not FileSystemManager.fileExists(kmzPath)):
		print("File does not exist: %s", kmzPath, )
		return filelist

	# Open zipped path and extract KML files
	filelist.extend(FileSystemManager.unzip(kmzPath, output_dir=kmzDir, overwrite=True))

	return filelist

def getKMLContent(kmlPath):
	""" Parse the KML file into a usable KML object """
	if (not FileSystemManager.fileExists(kmlPath)):
		print("KML file does not exist: %s", kmlPath, )
		return []

	print ("Reading KML file: %s" % kmlPath, )
	with open(kmlPath, 'r') as kmlFile:
		kmlContent = kmlFile.read()

	return kmlContent

def parseKMLPlacemarksFromContent(content):
	""" Parse the KML file from KML file content """
	kmlObj = kml.KML()
	kmlObj.from_string(content)

	features = list(kmlObj.features())

	if (len(features) != 1):
		print("Incorrect number of features: %d", len(features), )
		return []

	return list(features[0].features())

def getKMLPlacemarks(kmlFiles):
	""" Given a list of KML files, produce the corresponding KML 
		Placemarks from the set of files """
	placemarks = []

	for kmlFile in kmlFiles:
		placemarks.extend(parseKMLPlacemarksFromContent(getKMLContent(kmlFile)))

	formattedPlacemarks = []
	for placemark in placemarks:
		formattedPlacemarks.append(formatPlacemark(placemark))

	return formattedPlacemarks

def formatPlacemark(placemark):
	""" Format the placemark object for linesegments and values """
	status = "Closed" if CLOSED_COLOR in placemark.styleUrl else "Open"
	newPlacemark = Placemark(placemark.name, placemark.description, status=status, styleUrl=placemark.styleUrl)
	newPlacemark.line_segments.extend(getMultiGeometryLineSegments(placemark))

	# Get single line segment if not composed of multi geometry
	if len(newPlacemark.line_segments) == 0:
		newPlacemark.line_segments.extend(getLineSegment(placemark))

	return newPlacemark

def removeTagFormatting(tag):
	""" Remove kml tag formatting """
	return re.sub(r'{.*}', "", tag)

def getLineSegment(placemark):
	""" Get the line segment associated with a placemark """
	root = ET.fromstring(placemark.to_string().encode("utf8"))

	linesegmentNodes = [node for node in root if removeTagFormatting(node.tag) == "LineString"]

	# Parse each LineSegment
	linesegments = []
	for linesegmentNode in linesegmentNodes:
		linesegments.append(parseLineSegmentNode(linesegmentNode))

	return linesegments

def getMultiGeometryLineSegments(placemark):
	""" Get the line segments associated with a placemark """
	root = ET.fromstring(placemark.to_string().encode("utf8"))

	multigeometries = [node for node in root if removeTagFormatting(node.tag) == "MultiGeometry"]
	linesegmentNodes = []

	# Get LineSegments from MultiGeometries
	for multigeometry in multigeometries:
		linesegmentNodes.extend([node for node in multigeometry if removeTagFormatting(node.tag) == "LineString"])

	# Parse each LineSegment
	linesegments = []
	for linesegmentNode in linesegmentNodes:
		linesegments.append(parseLineSegmentNode(linesegmentNode))

	return linesegments

def parseLineSegmentNode(node):
	""" Parse the XML node to get coordinates associated with
		LineSegment """
	linesegment = LineSegment()
	coordinateNodes = [coords for coords in node if removeTagFormatting(coords.tag) == "coordinates"]
	double_re = "[-+]?\d+\.\d+"

	# Go through coordinates tags
	for coordinates in coordinateNodes:
		# Find all: lat,lng,elev in coordinates tag
		all_coords_str = coordinates.text
		coords_str = re.findall(double_re + "," + double_re + "," + double_re, 
			all_coords_str)
		# Go through matches, split, and parse
		for coords in coords_str:
			coords_vals = coords.rsplit(',')
			lng = float(coords_vals[0])
			lat = float(coords_vals[1])
			elev = float(coords_vals[2])
			linesegment.coordinates.append(Coordinate(lat, lng, elev))

	return linesegment

def constructKMLFromPlacemarks(placemarks, kmlPath):
	""" Construct KML content for placemarks """
	kml_content = kml.KML()
	namespace = "{http://www.opengis.net/kml/2.2}"

	# Get style maps and styles
	kmlObj = kml.KML()
	kmlObj.from_string(getKMLContent(kmlPath))
	styles = list(kmlObj.features())[0].styles()

	# Create document
	document = kml.Document(namespace, None, 'The Rivanna Trail', None, styles=styles)
	kml_content.append(document)

	for pm in placemarks:
		placemark = kml.Placemark(namespace, None, name=pm.name, description=pm.description, styleUrl=pm.styleUrl)

		linestrings = [lineseg.getOutputLineString() for lineseg in pm.line_segments]
		placemark.geometry = MultiLineString(linestrings)

		# Append to document
		if len(linestrings) > 0:
			document.append(placemark)

	return kml_content
