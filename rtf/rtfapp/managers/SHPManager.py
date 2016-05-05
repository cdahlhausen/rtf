# Manager system for interacting with SHP (zipped) files
from . import FileSystemManager
from rtfapp.managers.LocationObjects import Parcel, Placemark, Atom, LineSegment, Coordinate
from shapely.geometry import Point, MultiPoint, Polygon
from geopy.distance import vincenty
import openpyxl

import shapefile
import re
from math import sqrt
import os.path


def getRecordsAndFields(path, sType):
	records = []
	fields = []
	sf = shapefile.Reader(path)
	records = sf.records() if sType == 'point' else sf.shapeRecords()
	fields = sf.fields[1:] #Remove Deletion flag from the field list
	return [records, fields]


def parseCityParcels(pointRF, areaRF):
	""" Parse the SHP file into a usable shapefile object """
	parcels = {}
	idName = 'PROP_ID'

	for rec in pointRF[0]:
		parcelId = ''
		owner = ''
		prop_address = ''
		zipcode = ''
		for ind, field in enumerate(rec):
			if pointRF[1][ind][0] == idName:
				parcelId = field
			elif pointRF[1][ind][0] == 'OWNER':
				owner = field
			elif pointRF[1][ind][0] == 'ADDRESS':
				prop_address = field
			elif pointRF[1][ind][0] == 'ZIPCODE':
				zipcode = field

		address = ", ".join(filter(lambda x: x is not None and x != "", [prop_address, "Charlottesville", zipcode]))
		parcels[parcelId] = Parcel(parcelId, owner, "city", address=address)

	idName = 'PIN'

	for rec in areaRF[0]:
		parcelId = ''
		for ind, field in enumerate(rec.record):
			if areaRF[1][ind][0] == idName:
				parcelId = field
				break
		if parcelId in parcels:
			parcels[parcelId].addPoints(rec.shape.points, 1) # 0 for lat long, 1 nad83, City has nad83 so we use 1 here

	result = [value for key, value in parcels.iteritems()]
	return result



def getCountyParcels(areaFiles, excelFiles):
	areaPath = getShpFileName(areaFiles, prefix="Stacked_current")
	excelPath = getExcelFileName(excelFiles)
	pDict = getParcelsFromExcel(excelPath)
	# for key, value in pDict.iteritems():
	# 	print(value.id + ": " + value.owner)
	records = getRecordsAndFields(areaPath, 'area')

	for record in records[0]:
		parcelId = ''
		for index, field in enumerate(record.record):
			if records[1][index][0] == 'GPIN':
				parcelId = field
				break
		if parcelId in pDict:
			pDict[parcelId].addPoints(record.shape.points, 1)
	result = [value for key,value in pDict.iteritems()]
	return result




def getParcelsFromExcel(excelPath):
	""" Creates a dictionary of parcels from county excel path """
	parcels = {}

	if not os.path.isfile(excelPath):
		print('File does not exist: ' + excelPath)
		return parcels

	if excelPath[-4:] != 'xlsx':
		print('File is not xlsx: ' + excelPath)
		return parcels

	
	# Consider getting these dynamically from wb
	gpinIndex = 1
	ownerIndex = 4
	propStreet = 8
	city = 10
	zipcode = 11

	wb = openpyxl.load_workbook(excelPath)
	sheetName = wb.get_sheet_names()[0]
	sheet = wb.get_sheet_by_name(sheetName)
	for rIndex, row in enumerate(sheet.iter_rows(row_offset=1)):
		owner = row[ownerIndex].value
		gpin = row[gpinIndex].value
		address = ", ".join(filter(lambda x: x is not None and x != "", [row[propStreet].value, row[city].value, row[zipcode].value]))
		if owner is not None and gpin is not None:
			parcel = Parcel(pid=gpin, owner=owner, p_type="county", address=address)
			parcels[gpin] = parcel

	return parcels


def getShpFileName(shpFiles, prefix=''):
	result = ''
	pr_len = len(prefix)
	for f in shpFiles:
		if f[-4-pr_len:] == (prefix+'.shp'):
			result = f
			break
	return result


def getExcelFileName(files):
	result = ''
	for f in files:
		if f[-4:] == 'xlsx':
			result = f
			break
	return result


def getParcels(pointFiles, areaFiles):
	""" Given a list of files, produce the corresponding
	Parcel from the set of files """
	pointPath = getShpFileName(pointFiles)
	areaPath = getShpFileName(areaFiles)

	if not FileSystemManager.fileExists(pointPath) or not FileSystemManager.fileExists(areaPath):
		print("SHP file does not exist")
		return []

	pointRF = getRecordsAndFields(pointPath, 'point')
	areaRF = getRecordsAndFields(areaPath, 'area')
	parcels = []
	parcels.extend(parseCityParcels(pointRF, areaRF))
	return parcels

def distance(x1, y1, x2, y2):
	return sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))

def getMidpoint(x1, y1, x2, y2):
	return ((x1+x2)/2, (y1+y2)/2)

def getIntersections(ls, p1, parcels):
	""" Returns list of intersection points sorted by 
	distance from the first point in a line segment"""
	intersections = []
	for p in parcels:
		i = ls.intersection(p.linearRing)
		if type(i) is MultiPoint:
			points = [p for p in i.geoms]
		elif type(i) is Point:
			points = [i]
		else:
			continue

		# If distance too large, project and interpolate
		epsilonValue = 0.000001
		for point in points:
			if ls.distance(point) > epsilonValue:
				point = ls.interpolate(ls.project(point))

		distances = [(point.x, point.y, distance(point.x, point.y, p1[0], p1[1])) for point in points \
			if ls.distance(point) <= epsilonValue]
		intersections.extend(distances)
	i_s = list(set(intersections))        # Intersection set (no duplicates)
	# Sort the list
	i_s.sort(key=lambda x: x[2])

	return i_s	

			
def atomize_placemark(pm, parcels):
	placemark_segments = []
	full_possible_parcels = []
	for segment in pm.line_segments:
		intersect_parcel(segment, parcels, full_possible_parcels, placemark_segments)
	full_possible_parcels = list(set(full_possible_parcels)) # Remove duplicates
	pm.generateAtoms(placemark_segments)
	#Associate new atoms with parcels
	for atom in pm.atoms:
		for parcel in full_possible_parcels:            
			if atom.inParcel(parcel):
				atom.setParcel(parcel)
				parcel.on_trail = True			

def intersect_parcel(segment, parcels, full_possible_parcels, placemark_segments):
	new_segment_lines = []
	possible_parcels = []

	for parcel in parcels:                                 
		i = segment.getLineString().intersection(parcel.linearRing)
		#print segment.getLineString()
		if type(i) is Point or type(i) is MultiPoint:  # There was an intersection                           
			possible_parcels.append(parcel)

		# update distance of parcel to trail segment if < stored
		parcel_center = (parcel.linearRing.centroid.x, parcel.linearRing.centroid.y)

		for seg_point in [x.getCoords() for x in segment.coordinates]:
			parcel.distance_to_trail = min(parcel.distance_to_trail, vincenty(parcel_center, seg_point).meters)

	# If parcels, intersect, else just add lines
	if len(possible_parcels) > 0:
		for line in segment.getLines():           # LineStrings created from the coordinates in the LineSegment 
			new_line = LineSegment()
			first_point = line.coords[0]
			last_point = line.coords[1]

			i_s = getIntersections(line, first_point, possible_parcels)
			new_points = [Coordinate(first_point[0], first_point[1], 0)] + \
				map(lambda x: Coordinate(x[0], x[1], 0), i_s) + \
				[Coordinate(last_point[0], last_point[1], 0)]

			new_line.coordinates.extend(new_points)
			new_segment_lines.append(new_line)
		full_possible_parcels.extend(possible_parcels)
	else:
		for line in segment.getLines():
			new_line = LineSegment()

			first_point = line.coords[0]
			last_point = line.coords[1]

			new_points = [Coordinate(first_point[0], first_point[1], 0)] + \
				[Coordinate(last_point[0], last_point[1], 0)]

			new_line.coordinates.extend(new_points)
			new_segment_lines.append(new_line)
	# Add segments that are composed of atoms
	placemark_segments.append(new_segment_lines)