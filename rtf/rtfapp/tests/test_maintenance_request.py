from django.test import TestCase
from django.test.client import Client
from rtfapp.models import MaintenanceRequest, TrailSegment

import json

c = Client()

class MaintenanceRequestTests(TestCase):
	""" Test cases for Maintenance Requests """
	fixtures = ["test_maintenance_request_with_one_trail_segment.json"]

	def test_loadMaintenanceRequestFixures(self):
		""" Test using a fixture for a Maintenance Request by checking that data can be loaded """
		request = MaintenanceRequest.objects.get(pk=1)
		self.assertEquals(request.description, "This is a test maintenance request")

	def test_get_m_requests_no_filters(self):
		""" Test that getting trail json data works """		
		response = c.get('/maintenance-requests/')
		content = json.loads(response.content)
		m_request = content[0]['fields']
		self.assertEqual(m_request["resolved"], False)
		self.assertEqual(m_request["description"], "This is a test maintenance request")
		self.assertEqual(m_request["created_by"], "Michael")
		self.assertEqual(m_request["location"], "0,0")

	def test_get_m_requests_with_filters_not_filtered(self):
		""" Test that getting maintenance request json data works """		
		response = c.get('/maintenance-requests/?created_by=Michael')
		content = json.loads(response.content)
		m_request = content[0]['fields']
		self.assertEqual(m_request["resolved"], False)
		self.assertEqual(m_request["description"], "This is a test maintenance request")
		self.assertEqual(m_request["created_by"], "Michael")
		self.assertEqual(m_request["location"], "0,0")

	def test_get_m_requests_with_filters_filtered(self):
		""" Test that getting maintenance request json data with filter works """		
		response = c.get('/maintenance-requests/?created_by=Kyle')
		content = json.loads(response.content)
		self.assertEqual(len(content), 0)

	def test_edit_fail_invalid_info(self):
		""" Test that success is false when not all fields are provided """
		json_data = {
			"description": "Something",
			"created_by": "Kyle",
		}
		response = c.post('/maintenance-requests/1/', data=json_data)
		self.assertEqual(MaintenanceRequest.objects.get(pk=1).created_by, "Michael")

	def test_edit_success(self):
		""" Test that success is true when all fields are provided """
		json_data = {
			"description": "Something",
			"user": "Kyle",
			"latitude": "1",
			"longitude": "0",
			"resolved": "False"
		}
		response = c.post('/maintenance-requests/1/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], True)		
		self.assertEqual(MaintenanceRequest.objects.get(pk=1).created_by, "Kyle")

	def test_edit_resolve(self):
		""" Test that success is true when all fields are provided """
		json_data = {
			"resolved": "True"
		}
		response = c.post('/maintenance-requests/1/', data=json_data)
		content = json.loads(response.content)
		self.assertEqual(content['success'], True)		
		self.assertEqual(MaintenanceRequest.objects.get(pk=1).resolved, True)

	def test_mrequest_create_success(self):
		""" Test that creating a maintenance request works """
		json_data = {
			"description": "Something",
			"user": "Kyle",
			"latitude": "1",
			"longitude": "0"
		}
		response = c.post('/maintenance-requests/', data=json_data)	
		content = json.loads(response.content)
		m_request = MaintenanceRequest.objects.filter(created_by='Kyle').first()
		self.assertNotEqual(m_request, None)
		self.assertEqual(content['success'], True)

	def test_mrequest_create_failure(self):
		""" Test that success is false when not all fields are provided for create"""
		json_data = {
			"description": "Something",
			"user": "Kyle",
			"latitude": "1",
		}
		response = c.post('/maintenance-requests/', data=json_data)
		content = json.loads(response.content)
		try:
			m_request = MaintenanceRequest.objects.get(pk=2)
		except MaintenanceRequest.DoesNotExist:
			m_request = None
		self.assertEqual(m_request, None)
		self.assertEqual(content['success'], False)

	def test_mrequest_delete_valid_pk(self):
		""" Test deleting a maintenance request with a valid pk"""		
		response = c.delete('/maintenance-requests/1/')	

		try:
			m_request = MaintenanceRequest.objects.get(pk=1)
		except MaintenanceRequest.DoesNotExist:
			m_request = None
		self.assertEqual(m_request, None)		

	def test_mrequest_delete_invalid_pk(self):
		""" Test deleting a maintenance request with an invalid pk"""			
		response = c.delete('/maintenance-requests/3/')

		content = json.loads(response.content)
		self.assertEqual(content['success'], False)
