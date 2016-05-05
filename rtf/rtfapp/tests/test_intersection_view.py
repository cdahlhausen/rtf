from django.test import TestCase
from rtfapp.models import IntersectionTask
from datetime import timedelta, datetime
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rtfapp.managers import FileSystemManager
import json,os

timestamp_format = "%m-%d-%Y_%H-%M-%S"


c = Client()
class IntersectionTaskTests(TestCase):
	fixtures = ['users.json', 'user_profiles.json']
	
	def test_queue_intersection_get_task_no_task(self):	
		#login required
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/queue-intersection/')
		self.assertEqual(response.status_code, 200)
		test_task = json.loads(response.content)
		self.assertEquals(test_task["taskId"], -1)

	def test_queue_intersection_get_task_with_task(self):
		#login required
		first_time = datetime.now() - timedelta(seconds=10)
		intersection = IntersectionTask(pk=0, placemarks_completed=0, placemarks=3, started=first_time)
		intersection.save()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/queue-intersection/')
		self.assertEqual(response.status_code, 200)
		test_task = json.loads(response.content)
		self.assertEquals(test_task["taskId"], 0)

	# def test_queue_intersection_create_task_point_files(self):
	# 	response = c.post('/login/', {'username':'root', 'password': 'toor'})
	# 	p_files = SimpleUploadedFile("points.zip", "file_content", content_type="application/zip")
	# 	intersection_data = {'pointFiles': p_files}	
	# 	response = c.post('/queue-intersection/', intersection_data)
	# 	test_task = json.loads(response.content)
	# 	self.assertEquals(test_task["taskId"], 1)
	# 	cityPointsDir = FileSystemManager.fromHomeDir("cityPoints/")
	# 	cityPointFilePath = FileSystemManager.findLatestFile(cityPointsDir, ".zip", timestamp_format)
	# 	os.remove(cityPointFilePath)

	# def test_queue_intersection_create_task_other_files(self):
	# 	response = c.post('/login/', {'username':'root', 'password': 'toor'})
	# 	a_files = SimpleUploadedFile("testareas.zip", "file_content", content_type="application/zip")
	# 	#kmz_file = SimpleUploadedFile("testkml.kmz", "file_content", content_type="application/vnd.google-earth.kmz")
	# 	cs_files = SimpleUploadedFile("testcshapes.zip", "file_content", content_type="application/zip")
	# 	ce_files = SimpleUploadedFile("testcexcels.zip", "file_content", content_type="application/zip")
	# 	intersection_data = {'areaFiles': a_files, "countyShpFiles": cs_files, "countyExcelFiles": ce_files}
	# 	response = c.post('/queue-intersection/', intersection_data)
	# 	test_task = json.loads(response.content)
	# 	self.assertEquals(test_task["taskId"], 1)

	# 	#clean up files
	# 	cityAreasDir = FileSystemManager.fromHomeDir("cityAreas/")
	# 	kmzDir = FileSystemManager.fromHomeDir("kmz/")
	# 	countyAreasDir = FileSystemManager.fromHomeDir("countyAreas/")
	# 	countyExcelDir = FileSystemManager.fromHomeDir("countyExcel/")
	# 	filePath = FileSystemManager.findLatestFile(cityAreasDir, ".zip", timestamp_format)
	# 	os.remove(filePath)
	# 	# filePath = FileSystemManager.findLatestFile(kmzDir, ".kmz", timestamp_format)
	# 	# os.remove(filePath)
	# 	filePath = FileSystemManager.findLatestFile(countyAreasDir, ".zip", timestamp_format)
	# 	os.remove(filePath)
	# 	filePath = FileSystemManager.findLatestFile(countyExcelDir, ".zip", timestamp_format)
	# 	os.remove(filePath)

	# def test_intersection_task(self):
	# 	self.assertEquals(0,0)