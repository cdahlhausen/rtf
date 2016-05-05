from django.test import TestCase
from rtfapp.managers import LocationObjects

import fastkml
import json
import os
from os import path
from shapely.geometry import LineString



class LocationObjectsTests(TestCase):
	""" Test cases for the KMZ Manager """

	def test_formatCoordinateString(self):
		# Create test objects
		points = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)]

		# Perform test
		self.assertEqual(LocationObjects.formatCoordinateString(points), "0.0,0.0 0.0,1.0 1.0,1.0 1.0,0.0")

	def test_Coordinate_init(self):
		coord = LocationObjects.Coordinate(78.69,453.45, 25)
		self.assertEqual(coord.latitude,78.69)
		self.assertEqual(coord.longitude,453.45)
		self.assertEqual(coord.elevation, 25)

	def test_LineSegment_init(self):
		line = LocationObjects.LineSegment()
		self.assertEqual(line.coordinates, [])

	def test_Placemark_init(self):
		mark = LocationObjects.Placemark("name", "Description of placemark")
		self.assertEqual(mark.name, "name")
		self.assertEqual(mark.description, "Description of placemark")

	def test_Parcel_init(self):
		p = LocationObjects.Parcel(1, "tester", "city")
		self.assertEqual(p.id, 1)
		self.assertEqual(p.owner, "tester")
		self.assertEqual(p.p_type, "city")
		self.assertIsNone(p.linearRing)
	
	def test_Parcel_addPoints(self):
		p = LocationObjects.Parcel(1, "tester", "city")
		p.addPoints([(37,-70),(37.2, -70),(37.5, -71),(37, -71)], 0)
		self.assertEqual(len(p.points), 4)
		self.assertEqual(p.points[0], (37, -70))
		self.assertIsNotNone(p.linearRing)

	def test_convertCoords(self):
		points = [(11487379.57183, 3547757.431121), (10959709.13514, 3573134.644992)]
		actual = [(37.066463371013, -78.484703829535), (37.122504968226, -80.294680214927)]
		parcel = LocationObjects.Parcel(1, "testOwner", "city")
		test = parcel.convertCoords(points)
		self.assertAlmostEquals(test[0][0], actual[0][0], 2)
		self.assertAlmostEquals(test[0][1], actual[0][1], 2)
		self.assertAlmostEquals(test[1][0], actual[1][0], 2)
		self.assertAlmostEquals(test[1][1], actual[1][1], 2)

	def test_LineString_getLineString(self):
		# Create test objects
		coordinates = [LocationObjects.Coordinate(1.0, 2.0, 3.0), LocationObjects.Coordinate(2.0, 3.0, 4.0), \
			LocationObjects.Coordinate(3.0, 4.0, 5.0)]
		line_segment = LocationObjects.LineSegment()
		line_segment.coordinates = coordinates

		# Perform test
		line_string = line_segment.getLineString()
		self.assertEqual(line_string.coords[0], (1.0, 2.0))
		self.assertEqual(line_string.coords[1], (2.0, 3.0))
		self.assertEqual(line_string.coords[2], (3.0, 4.0))

	def test_LineString_getLines_singleLine(self):
		# Create test objects
		coordinates = [LocationObjects.Coordinate(1.0, 2.0, 3.0), LocationObjects.Coordinate(2.0, 3.0, 4.0)]
		line_segment = LocationObjects.LineSegment()
		line_segment.coordinates = coordinates

		# Perform test
		lines_list = line_segment.getLines()
		self.assertEqual(lines_list[0].coords[0], (1.0, 2.0))
		self.assertEqual(lines_list[0].coords[1], (2.0, 3.0))

	def test_LineString_getLines_multipleLines(self):
		# Create test objects
		coordinates = [LocationObjects.Coordinate(1.0, 2.0, 3.0), LocationObjects.Coordinate(2.0, 3.0, 4.0), \
			LocationObjects.Coordinate(3.0, 4.0, 5.0), LocationObjects.Coordinate(4.0, 5.0, 6.0)]
		line_segment = LocationObjects.LineSegment()
		line_segment.coordinates = coordinates

		# Perform test
		lines_list = line_segment.getLines()
		self.assertEqual(lines_list[0].coords[0], (1.0, 2.0))
		self.assertEqual(lines_list[0].coords[1], (2.0, 3.0))
		self.assertEqual(lines_list[1].coords[0], (2.0, 3.0))
		self.assertEqual(lines_list[1].coords[1], (3.0, 4.0))
		self.assertEqual(lines_list[2].coords[0], (3.0, 4.0))
		self.assertEqual(lines_list[2].coords[1], (4.0, 5.0))

	def test_Atom_setParcel_singleParcel(self):
		# Create test objects
		parcel = LocationObjects.Parcel(0, "Michael", "city")
		parcel.addPoints([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], coordType=0)
		atom = LocationObjects.Atom(linestring=None, placemark=None)

		# Perform test
		atom.setParcel(parcel)
		self.assertEqual(atom.parcel, parcel)

	def test_Atom_setParcel_multipleParcelPickLargerArea(self):
		# Create test objects
		parcel = LocationObjects.Parcel(0, "Michael", "city")
		parcel.addPoints([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], coordType=0)
		parcel2 = LocationObjects.Parcel(1, "Michael", "city")
		parcel2.addPoints([(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0)], coordType=0)
		parcel3 = LocationObjects.Parcel(2, "Michael", "city")
		parcel3.addPoints([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], coordType=0)
		atom = LocationObjects.Atom(linestring=None, placemark=None)

		# Perform test
		atom.setParcel(parcel)
		atom.setParcel(parcel2)
		atom.setParcel(parcel3)
		self.assertEqual(atom.parcel, parcel2)

	def test_Atom_inParcel_lineInParcel(self):
		# Create test objects
		parcel = LocationObjects.Parcel(0, "Michael", "city")
		parcel.addPoints([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], coordType=0)
		line_string = LineString([(0.0, 0.5), (1.0, 0.5)])
		atom = LocationObjects.Atom(linestring=line_string, placemark=None)

		# Perform test
		self.assertEqual(atom.inParcel(parcel), True)

	def test_Atom_inParcel_lineOutsideParcel(self):
		# Create test objects
		parcel = LocationObjects.Parcel(0, "Michael", "city")
		parcel.addPoints([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], coordType=0)
		line_string = LineString([(-1.0, 0.5), (0.0, 0.5)])
		atom = LocationObjects.Atom(linestring=line_string, placemark=None)

		# Perform test
		self.assertEqual(atom.inParcel(parcel), False)

	def test_Atom_formatCoordinates(self):
		# Create test objects
		line_string = LineString([(0.0, 0.0), (1.0, 1.0)])
		atom = LocationObjects.Atom(linestring=line_string, placemark=None)

		# Perform test
		self.assertEqual(atom.formatCoordinates(), "0.0,0.0 1.0,1.0")

	def test_Placemark_generateAtoms(self):
		coordinates = [LocationObjects.Coordinate(1.0, 2.0, 3.0), LocationObjects.Coordinate(2.0, 3.0, 4.0)]
		line_segment = LocationObjects.LineSegment()
		line_segment.coordinates = coordinates

		coordinates_1 = [LocationObjects.Coordinate(7.0, 8.0, 1.0), LocationObjects.Coordinate(1.0, 3.0, 5.0)]
		line_segment_1 = LocationObjects.LineSegment()
		line_segment_1.coordinates = coordinates_1

		line_segments = [[line_segment, line_segment_1]]
		mark = LocationObjects.Placemark("name", "Description of placemark")
		mark.generateAtoms(line_segments)

		self.assertEqual("1.0,2.0 2.0,3.0", mark.atoms[0].formatCoordinates())
		self.assertEqual("7.0,8.0 1.0,3.0", mark.atoms[1].formatCoordinates())

	def test_Placemark_generateAtoms_noSegment(self):
		coordinates = [LocationObjects.Coordinate(1.0, 2.0, 3.0)]
		line_segment = LocationObjects.LineSegment()
		line_segment.coordinates = coordinates

		coordinates_1 = [LocationObjects.Coordinate(7.0, 8.0, 1.0)]
		line_segment_1 = LocationObjects.LineSegment()
		line_segment_1.coordinates = coordinates_1

		line_segments = [[line_segment, line_segment_1]]
		mark = LocationObjects.Placemark("name", "Description of placemark")
		mark.generateAtoms(line_segments)

		self.assertEqual(0, len(mark.atoms))

	def test_Parcel_getSize(self):
		p = LocationObjects.Parcel(1, "tester", "city")
		p.addPoints([(37,-70),(37.2, -70),(37.5, -71),(37, -71)], 0)
		self.assertAlmostEquals(0.35, p.getSize())

	def test_Parcel_str(self):
		p = LocationObjects.Parcel(1, "tester", "city")
		p.addPoints([(37,-70),(37.2, -70),(37.5, -71),(37, -71)], 0)
		self.assertEqual(str(p), 'Owner: tester')