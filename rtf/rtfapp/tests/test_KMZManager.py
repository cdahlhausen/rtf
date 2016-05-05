from django.test import TestCase
from rtfapp.managers import KMZManager

from fastkml import kml
import json
from rtfapp.managers.LocationObjects import Placemark, LineSegment, Coordinate
import os
from os import path
from shapely.geometry import MultiLineString
import xml.etree.ElementTree as ET


def fromTestingDirToFixturesDir(path):
	""" Return the path from where tests are run to the fixtures dir """
	return "rtfapp/fixtures/" + path

def parseJsonFile(filepath):
	""" Parse the JSON file """
	with open(filepath) as openFile:
		fileContent = json.load(openFile)
	return fileContent

def readFromFile(filepath):
	""" Read the file content """
	with open(filepath) as openFile:
		content = openFile.read()
	return content

def generatePlacemarks(content):
	""" Generate KML placemarks list from content """
	kmlObj = kml.KML()
	kmlObj.from_string(content)
	features = list(kmlObj.features())
	return list(features[0].features()) if len(features) > 0 else []

def deleteDir(directory):
	""" Delete the extracted directory """
	home_dir = path.expanduser("~") + "/"
	for current_file in os.listdir(home_dir + directory):
		print "Deleting", current_file
		os.remove(home_dir + directory + "/" + current_file)
	print "Deleting", directory
	os.rmdir(home_dir + directory)


class KMZManagerTests(TestCase):
	""" Test cases for the KMZ Manager """
	def test_extractKMLFiles_bad_file(self):
		""" Test extracting a KML file from a bad file location """
		# Create test objects
		filename = "kml_non_existant_file"
		filepath = fromTestingDirToFixturesDir(filename + ".kmz")

		# Perform test
		result = KMZManager.extractKMLFiles(filepath)
		self.assertEqual(len(result), 0)

	def test_extractKMLFiles_kmz_file(self):
		""" Test extracting a KML file from a kmz file """
		# Create test objects
		filename = "test_kmz"
		filepath = fromTestingDirToFixturesDir(filename + ".kmz")

		# Perform test
		result = KMZManager.extractKMLFiles(filepath)
		self.assertEqual(len(result), 4)

		# Cleanup
		deleteDir(filename)

	def test_getKMLContent_bad_file(self):
		""" Test retrieving kml content """
		# Create test objects
		filepath = fromTestingDirToFixturesDir("test_kmz/non_existant.kml")

		# Perform test
		result = KMZManager.getKMLContent(filepath)
		self.assertEqual(len(result), 0)

	def test_getKMLContent_kml(self):
		""" Test retrieving kml content """
		# Create test objects
		filepath = fromTestingDirToFixturesDir("test_kmz/empty.kml")

		# Perform test
		result = KMZManager.getKMLContent(filepath)
		self.assertTrue(len(result) > 0)
		self.assertTrue("Empty Placemark Test Trail" in result)

	def test_parseKMLPlacemarksFromContent_no_features(self):
		""" Test retrieving kml content when no document feature """
		# Create test objects
		content = "<?xml version='1.0'?><kml xmlns='http://www.opengis.net/kml/2.2'></kml>"

		# Perform test
		result = KMZManager.parseKMLPlacemarksFromContent(content)
		self.assertEqual(len(result), 0)

	def test_parseKMLPlacemarksFromContent_singlePlacemarkTestTrail(self):
		""" Test extracting features from a test KML file with a single placemark """
		filepath = fromTestingDirToFixturesDir("kml_single_placemark_test_trail.json")
		fileContent = parseJsonFile(filepath)
		placemarks = KMZManager.parseKMLPlacemarksFromContent(fileContent["content"])

		self.assertEqual(len(placemarks), 1)
		self.assertEqual(placemarks[0].name, "Placemark 1")
		self.assertEqual(placemarks[0].description, "Placemark 1 Description")

	def test_parseKMLPlacemarksFromContent_emptyPlacemarkTestTrail(self):
		""" Test extracting features from a test KML file with no placemarks """
		filepath = fromTestingDirToFixturesDir("kml_empty_placemark_test_trail.json")
		fileContent = parseJsonFile(filepath)
		placemarks = KMZManager.parseKMLPlacemarksFromContent(fileContent["content"])

		self.assertEqual(len(placemarks), 0)

	def test_getKMLPlacemarks_single_empty_kml(self):
		""" Test getting placemarks from an empty KML file """
		# Create test objects
		files = [fromTestingDirToFixturesDir("test_kmz/empty.kml")]

		# Perform test
		result = KMZManager.getKMLPlacemarks(files)
		self.assertEqual(len(result), 0)

	def test_getKMLPlacemarks_single_kml(self):
		""" Test getting placemarks from a single KML file """
		# Create test objects
		files = [fromTestingDirToFixturesDir("test_kmz/single_placemark.kml")]

		# Perform test
		result = KMZManager.getKMLPlacemarks(files)
		self.assertEqual(len(result), 1)
		self.assertTrue("Placemark 1" in result[0].name)

	def test_getKMLPlacemarks_multiple_kml(self):
		""" Test getting placemarks from an empty KML file and a filled KML file"""
		# Create test objects
		files = [fromTestingDirToFixturesDir("test_kmz/empty.kml"), \
			fromTestingDirToFixturesDir("test_kmz/single_placemark.kml")]

		# Perform test
		result = KMZManager.getKMLPlacemarks(files)
		self.assertEqual(len(result), 1)
		self.assertTrue("Placemark 1" in result[0].name)

	def test_formatPlacemark_open_with_multigeometry(self):
		""" Test formatting an open multigeometry placemark """
		# Create test objects
		content = readFromFile(fromTestingDirToFixturesDir("test_kmz/single_placemark.kml"))
		placemarks = generatePlacemarks(content)

		# Perform test
		self.assertEqual(len(placemarks), 1)
		formatted_placemark = KMZManager.formatPlacemark(placemarks[0])
		self.assertEqual(formatted_placemark.status, "Open")
		self.assertTrue("Placemark 1 Description" in formatted_placemark.description)
		self.assertTrue("Placemark 1" in formatted_placemark.name)
		self.assertEqual("#line-000000-1", formatted_placemark.styleUrl)
		self.assertEqual(len(formatted_placemark.line_segments), 1)
		self.assertEqual(len(formatted_placemark.line_segments[0].coordinates), 7)

	def test_formatPlacemark_closed_with_linestring(self):
		""" Test formatting a closed linestring placemark """
		# Create test objects
		content = readFromFile(fromTestingDirToFixturesDir("test_kmz/single_linestring.kml"))
		placemarks = generatePlacemarks(content)

		# Perform test
		self.assertEqual(len(placemarks), 1)
		formatted_placemark = KMZManager.formatPlacemark(placemarks[0])
		self.assertEqual(formatted_placemark.status, "Closed")
		self.assertTrue("Placemark 1 Description" in formatted_placemark.description)
		self.assertTrue("Placemark 1" in formatted_placemark.name)
		self.assertEqual("#line-FF0000-1", formatted_placemark.styleUrl)
		self.assertEqual(len(formatted_placemark.line_segments), 1)
		self.assertEqual(len(formatted_placemark.line_segments[0].coordinates), 7)

	def test_formatPlacemark_closed_with_multiple_linestrings(self):
		""" Test formatting a closed multigeometry with multiple linestrings placemark """
		# Create test objects
		content = readFromFile(fromTestingDirToFixturesDir("test_kmz/multiple_linestrings_in_multigeometry.kml"))
		placemarks = generatePlacemarks(content)

		# Perform test
		self.assertEqual(len(placemarks), 1)
		formatted_placemark = KMZManager.formatPlacemark(placemarks[0])
		self.assertEqual(formatted_placemark.status, "Closed")
		self.assertTrue("Placemark 1 Description" in formatted_placemark.description)
		self.assertTrue("Placemark 1" in formatted_placemark.name)
		self.assertEqual("#line-FF0000-1", formatted_placemark.styleUrl)
		self.assertEqual(len(formatted_placemark.line_segments), 2)
		self.assertEqual(len(formatted_placemark.line_segments[0].coordinates), 7)
		self.assertEqual(len(formatted_placemark.line_segments[1].coordinates), 6)

	def test_removeTagFormatting_with_kml_tag(self):
		""" Test removing a kml formatted xml tag """
		# Create test objects
		xml_tag = "{http://www.opengis.net/kml/2.2}LineString"
		xml_expected = "LineString"

		# Perform test
		formatted_tag = KMZManager.removeTagFormatting(xml_tag)
		self.assertEqual(xml_expected, formatted_tag)

	def test_removeTagFormatting_without_kml_tag(self):
		""" Test removing a non-kml formatted xml tag """
		# Create test objects
		xml_tag = "LineString"
		xml_expected = "LineString"

		# Perform test
		formatted_tag = KMZManager.removeTagFormatting(xml_tag)
		self.assertEqual(xml_expected, formatted_tag)

	def test_getLineSegment(self):
		""" Test parsing a line segment from a placemark """
		# Create test objects
		content = readFromFile(fromTestingDirToFixturesDir("test_kmz/single_linestring.kml"))
		placemarks = generatePlacemarks(content)

		# Perform test
		self.assertEqual(len(placemarks), 1)
		linesegments = KMZManager.getLineSegment(placemarks[0])
		self.assertEqual(len(linesegments), 1)
		self.assertEqual(len(linesegments[0].coordinates), 7)

	def test_getMultiGeometryLineSegments(self):
		""" Test parsing multi geometry line segments from a placemark """
		# Create test objects
		content = readFromFile(fromTestingDirToFixturesDir("test_kmz/single_placemark.kml"))
		placemarks = generatePlacemarks(content)

		# Perform test
		self.assertEqual(len(placemarks), 1)
		linesegments = KMZManager.getMultiGeometryLineSegments(placemarks[0])
		self.assertEqual(len(linesegments), 1)
		self.assertEqual(len(linesegments[0].coordinates), 7)

	def test_parseLineSegmentNode(self):
		""" Test parsing a line segment from a LineString node """
		# Create test objects
		xml_linestring = "<LineString><coordinates>0.0,0.0,0.0</coordinates><coordinates>1.0,0.0,0.0 0.0,1.0,0.0 0.0,0.0,1.0</coordinates></LineString>"
		node = ET.fromstring(xml_linestring)

		# Perform test
		line_segment = KMZManager.parseLineSegmentNode(node)
		self.assertEqual(len(line_segment.coordinates), 4)
		self.assertEqual(line_segment.coordinates[0].longitude, 0.0)
		self.assertEqual(line_segment.coordinates[0].latitude, 0.0)
		self.assertEqual(line_segment.coordinates[0].elevation, 0.0)
		self.assertEqual(line_segment.coordinates[1].longitude, 1.0)
		self.assertEqual(line_segment.coordinates[1].latitude, 0.0)
		self.assertEqual(line_segment.coordinates[1].elevation, 0.0)
		self.assertEqual(line_segment.coordinates[2].longitude, 0.0)
		self.assertEqual(line_segment.coordinates[2].latitude, 1.0)
		self.assertEqual(line_segment.coordinates[2].elevation, 0.0)
		self.assertEqual(line_segment.coordinates[3].longitude, 0.0)
		self.assertEqual(line_segment.coordinates[3].latitude, 0.0)
		self.assertEqual(line_segment.coordinates[3].elevation, 1.0)

	def test_constructKMLFromPlacemarks(self):
		""" Test constructing a KML from a set of placemarks """
		# Create test objects
		kmlPath = fromTestingDirToFixturesDir("test_kmz/empty.kml")

		placemark1 = Placemark("Placemark 1", "Placemark 1 Description")
		placemark1.line_segments.append(LineSegment())
		placemark1.line_segments[0].coordinates = [Coordinate(0.0, 0.0, 0.0), Coordinate(1.0, 1.0, 1.0)]
		placemark1.line_segments.append(LineSegment())
		placemark1.line_segments[1].coordinates = [Coordinate(0.0, 0.0, 1.0), Coordinate(0.0, 1.0, 0.0), Coordinate(1.0, 0.0, 0.0)]

		placemark2 = Placemark("Placemark 2", "Placemark 2 Description")
		placemark2.line_segments.append(LineSegment())
		placemark2.line_segments[0].coordinates = [Coordinate(0.0, 1.0, 1.0), Coordinate(0.0, 0.0, 0.0)]

		placemarks = [placemark1, placemark2]

		# Perform test
		kml_content = KMZManager.constructKMLFromPlacemarks(placemarks, kmlPath)
		kml_features = list(kml_content.features())
		self.assertEqual(len(kml_features), 1)
		document = kml_features[0]
		self.assertEqual(document.name, "The Rivanna Trail")
		kml_placemarks = list(document.features())
		self.assertEqual(len(kml_placemarks), 2)

		# ... Placemark 1
		self.assertEqual(kml_placemarks[0].name, "Placemark 1")
		self.assertEqual(kml_placemarks[0].description, "Placemark 1 Description")
		self.assertEqual(len(kml_placemarks[0].geometry.geoms), 2)

		self.assertEqual(len(kml_placemarks[0].geometry.geoms[0].coords), 2)
		self.assertEqual(kml_placemarks[0].geometry.geoms[0].coords[0], (0.0, 0.0, 0.0))
		self.assertEqual(kml_placemarks[0].geometry.geoms[0].coords[1], (1.0, 1.0, 1.0))

		self.assertEqual(len(kml_placemarks[0].geometry.geoms[1].coords), 3)
		self.assertEqual(kml_placemarks[0].geometry.geoms[1].coords[0], (0.0, 0.0, 1.0))
		self.assertEqual(kml_placemarks[0].geometry.geoms[1].coords[1], (1.0, 0.0, 0.0))
		self.assertEqual(kml_placemarks[0].geometry.geoms[1].coords[2], (0.0, 1.0, 0.0))

		# ... Placemark 2
		self.assertEqual(kml_placemarks[1].name, "Placemark 2")
		self.assertEqual(kml_placemarks[1].description, "Placemark 2 Description")
		self.assertEqual(len(kml_placemarks[1].geometry.geoms), 1)

		self.assertEqual(len(kml_placemarks[1].geometry.geoms[0].coords), 2)
		self.assertEqual(kml_placemarks[1].geometry.geoms[0].coords[0], (1.0, 0.0, 1.0))
		self.assertEqual(kml_placemarks[1].geometry.geoms[0].coords[1], (0.0, 0.0, 0.0))