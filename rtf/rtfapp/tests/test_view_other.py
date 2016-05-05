from django.test import TestCase
from rtfapp.models import IntersectionTask
from datetime import timedelta, datetime
import time
import os
from os import path
from django.test.client import Client
from django.contrib.auth.models import User
from rtfapp.forms import UserForm, UserProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile

import json

def fromTestingDirToFixturesDir(path):
	""" Return the path from where tests are run to the fixtures dir """
	return "rtfapp/fixtures/" + path

def readFromFile(filepath):
	""" Read the file content """
	with open(filepath) as openFile:
		content = openFile.read()
	return content

def writeToFile(filepath, filecontent):
	""" Write the file content """
	with open(filepath, 'w') as fs:
		fs.write(filecontent)

def get_timestamp():
	""" Get the timestamp formatted """
	timestamp_format = "%m-%d-%Y_%H-%M-%S"
	return datetime.fromtimestamp(time.time()).strftime(timestamp_format)


c = Client()
class OtherViewTests(TestCase):
	fixtures = ['users.json', 'user_profiles.json']

	def test_index_login_redirect(self):	
		#login required
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/', follow=True)
		self.assertTrue("<title>Admin | Rivanna Trails Foundation</title>" in response.content)

	def test_register_post_valid_data(self):		
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		user_form_data = {'username': 'Kyle', 'email': 'kyle@kyle.com', 'password': 'password', 'phone_number': '555-5555'}
		response = c.post('/register/', user_form_data)
		self.assertFalse("<title>Register | Rivanna Trails Foundation</title>" in response.content)	
		self.assertTrue("<title>Admin | Rivanna Trails Foundation</title>" in response.content)	
		self.assertTrue("<b>User Kyle successfully registered.</b>" in response.content)


	def test_register_post_invalid_data(self):		
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		user_form_data = {'username': 'Kyle'}
		response = c.post('/register/', user_form_data)
		self.assertTrue("<h2>Errors</h2>" in response.content)

	def test_register_get_form(self):		
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/register/')
		self.assertTrue("<title>Register | Rivanna Trails Foundation</title>" in response.content)

	def test_edit_get_form(self):		
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/edit-profile/')
		self.assertTrue("<title>Edit User | Rivanna Trails Foundation</title>" in response.content)

	def test_edit_profile_post_valid_data_all(self):
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		user_form_data = {'username': 'Kyle', 'email': 'kyle@kyle.com', 'phone_number': '555-5555'}
		response = c.post('/edit-profile/', user_form_data)
		self.assertTrue("<title>Admin | Rivanna Trails Foundation</title>" in response.content)	
		self.assertTrue("<b>User profile for Kyle successfully edited.</b>" in response.content)
		user_form_data = {'username': 'John', 'email': 'john@kyle.com', 'phone_number': '555-1234'}
		response = c.post('/edit-profile/', user_form_data)
		self.assertTrue("<title>Admin | Rivanna Trails Foundation</title>" in response.content)	
		self.assertTrue("<b>User profile for John successfully edited.</b>" in response.content)

	def test_download_kmz(self):
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		# Create KMZ in kmz dir
		__dir = path.expanduser("~") + "/kmz/"
		if not path.exists(__dir):
			os.makedirs(__dir)
		current_file = __dir + get_timestamp() + ".kmz"
		writeToFile(current_file, readFromFile(fromTestingDirToFixturesDir("test_download_kmz.kmz")))

		response = c.get('/downloadKMZ/')
		self.assertEquals(response.get('Content-Disposition'), "attachment; filename=rivanna_trail.kmz")

		os.remove(current_file)


	
