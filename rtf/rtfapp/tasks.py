from __future__ import absolute_import

from celery import shared_task
from .managers import DBManager, FileSystemManager, SHPManager, KMZManager, LocationObjects
import time
from datetime import timedelta, datetime

# Celery tasks will go here
# @shared_task
# def test_task(id, num):
# 	# Wait 30 seconds to update parcels_extracted
# 	print id, num
# 	time.sleep(30)
# 	DBManager.edit_intersection_task(id, parcels_extracted=True)
# 	# Increment progress every 10 
# 	secs = 10
# 	for i in range(num):
# 		print i
# 		time.sleep(secs)
# 		DBManager.edit_intersection_task(id, placemark_time=timedelta(seconds=secs), placemarks_completed=i+1)
# 	# Finish
# 	DBManager.edit_intersection_task(id, finished=True)
# 	return None

@shared_task
def intersect_task(id, kmzFilePath, cityPointFilePath, areaFilePath, countyAreaFilePath, countyExcelFilePath):	
	cityPointsDir = FileSystemManager.fromHomeDir("cityPoints/")
	cityAreasDir = FileSystemManager.fromHomeDir("cityAreas/")
	countyAreasDir = FileSystemManager.fromHomeDir("countyAreas/")
	countyExcelDir = FileSystemManager.fromHomeDir("countyExcel/")

	# Extract SHP files, which saves to server file system
	pointFiles = FileSystemManager.unzip(cityPointFilePath, output_dir=cityPointsDir, overwrite=True)
	areaFiles = FileSystemManager.unzip(areaFilePath, output_dir=cityAreasDir, overwrite=True)		
	countyAreaFiles = FileSystemManager.unzip(countyAreaFilePath, output_dir=countyAreasDir, overwrite=True)
	countyExcelFiles = FileSystemManager.unzip(countyExcelFilePath, output_dir=countyExcelDir, overwrite=True)

	# Extract KML files
	kmz_dir = FileSystemManager.fromHomeDir("kmz/")	
	kml_files = KMZManager.extractKMLFiles(kmzFilePath, kmz_dir)		
	placemarks = KMZManager.getKMLPlacemarks(kml_files)
	
	parcels = SHPManager.getParcels(pointFiles, areaFiles)
	countyParcels = SHPManager.getCountyParcels(countyAreaFiles, countyExcelFiles)
	parcels.extend(countyParcels)

	# Update intersection task object in database
	DBManager.edit_intersection_task(id, parcels_extracted=True)		

	# Intersect all the placemarks with the parcels
	count = 0
	start_time = datetime.now()
	parcels = filter(lambda x: len(x.points) > 2, parcels)
	for pm in placemarks:
		SHPManager.atomize_placemark(pm, parcels)
		time_of_operation = datetime.now() - start_time
		count += 1
		# Update intersection task object in database
		DBManager.edit_intersection_task(id, placemark_time=time_of_operation, placemarks_completed=count)

	# Delete all placemarks, parcels, and atoms from database
	DBManager.deleteTrailData()

	# Save all parcels to db
	DBManager.save_parcels(parcels)

	# Store placemarks, parcels, and atoms
	DBManager.saveTrailData(placemarks)

	# Finish
	DBManager.edit_intersection_task(id, finished=True)
	return None
