from django.test import TestCase
from django.test.client import Client
from rtfapp.models import TrailSegment

import json

c = Client()
class TrailAnnotationsTest(TestCase):
	""" Test cases for trail annotations """
	fixtures = ['test_trail_annotation.json']
	
	def test_get_trails(self):
		""" Test that getting trail json data works """		
		response = c.get('/placemarks/')
		content = json.loads(response.content)
		placemark = content['placemarks'][0]
		self.assertEqual(placemark["status"], "Open")
		self.assertEqual(placemark["conditions"], "Good")
		self.assertEqual(placemark["name"], "Trail Segment 1")
		self.assertEqual(placemark["description"], "Test trail segment")

	def test_edit_fail_invalid_info(self):
		""" Test that success is false when not all fields are provided """
		json_data = {
			"status": "Open", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"id": 1
		}
		response = c.post('/placemarks/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], False)

	def test_edit_success(self):
		""" Test that success is true when all fields are provided """
		json_data = {
			"status": "Open", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"description": "Test trail segment",
			"id": 1
		}
		response = c.post('/placemarks/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], True)

	#check timestamp update
	def test_timestamp_update(self):
		""" Test that a successful post updates the last_edit """
		json_data = {
			"status": "Open", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"description": "Test trail segment",
			"id": 1
		}
		old_timestamp = TrailSegment.objects.get(pk=1).last_edit
		response = c.post('/placemarks/', data=json_data)
		new_timestamp = TrailSegment.objects.get(pk=1).last_edit
		self.assertTrue(new_timestamp > old_timestamp)

	def test_false_on_invalid_id(self):
		""" Test that an invalid id gives a 404 response """
		json_data = {
			"status": "Open", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"description": "Test trail segment",
			"id": 2
		}

		response = c.post('/placemarks/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], False)

	def test_color_update(self):
		""" Test that the style_url color is changed on status change """
		json_data = {
			"status": "Closed", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"description": "Test trail segment",
			"id": 1
		}
		response = c.post('/placemarks/', data=json_data)
		style_url = TrailSegment.objects.get(pk=1).style_url
		self.assertEqual(style_url, '#line-FF0000-3')

	def test_delete_failure(self):
		""" Test that delete always fails """
		json_data = {
			"status": "Closed", 
			"current_conditions": "Good", 
			"name": "Trail Segment 1", 
			"description": "Test trail segment",
			"id": 1
		}
		response = c.delete('/placemarks/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], False)