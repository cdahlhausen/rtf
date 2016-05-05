from django.test import TestCase
from rtfapp.managers import DBManager, LocationObjects
from rtfapp.models import MaintenanceRequest, TrailSegment, Parcel, Atom, UserProfile, IntersectionTask
from django.contrib.auth.models import User
from rtfapp.forms import UserForm, UserProfileForm
from datetime import timedelta, datetime

class DBManagerTests(TestCase):

	""" Test cases for the Database Manager """

	def test_deleteTrailData(self):
		""" Test deleting data stored for the trail """
		# Create test objects
		trail_seg = TrailSegment(name="Trail 1", description="Description...", trail_status='Open', style_url="")
		trail_seg.save()

		parcel = Parcel(pid='123', size=1.234, \
			owner="Owner", address="123 Fake Ln", on_trail=True, \
			points_string="0.0,0.0 0.0,1.0 1.0,1.0 1.0,0.0", parcel_type="city", \
			distance_to_trail=500, notes="Need permission",permissions="www.abc.com")
		parcel.save()

		atom = Atom(trail_segment=trail_seg, coordinates="0.0,0.0 1.0,1.0", parcel=parcel, \
			segment_id=0, position_id=0)
		atom.save()

		# Perform test
		DBManager.deleteTrailData()
		self.assertEqual(len(TrailSegment.objects.all()), 0)
		self.assertEqual(len(Parcel.objects.all()), 0)
		self.assertEqual(len(Atom.objects.all()), 0)

	def test_retrievePlacemarkData_multiple_trails_parcels_atoms(self):
		""" Test retrieving placemark data when multiple trails, parcels, and atoms exist """
		# Create test objects
		trail_seg_1 = TrailSegment(name="Trail 1", description="Description...", trail_status='Open', style_url="")
		trail_seg_1.save()

		trail_seg_2 = TrailSegment(name="Trail 2", description="Description...", trail_status='Open', style_url="")
		trail_seg_2.save()

		parcel = Parcel(pid='123', size=1.234, \
			owner="Owner", address="123 Fake Ln", on_trail=True, \
			points_string="0.0,0.0 0.0,1.0 1.0,1.0 1.0,0.0", parcel_type="city", \
			distance_to_trail=0, permissions="www.yahoo.com", notes="Need to renew permissions")
		parcel.save()

		# atom_trail#_segment#_position#
		atom_1_1_1 = Atom(trail_segment=trail_seg_1, coordinates="0.0,0.0 1.0,1.0", parcel=parcel, \
			segment_id=0, position_id=0)
		atom_1_1_1.save()

		atom_1_2_1 = Atom(trail_segment=trail_seg_1, coordinates="1.0,1.0 2.0,2.0", parcel=parcel, \
			segment_id=1, position_id=0)
		atom_1_2_1.save()

		atom_1_2_2 = Atom(trail_segment=trail_seg_1, coordinates="2.0,2.0 3.0,3.0", parcel=parcel, \
			segment_id=1, position_id=1)
		atom_1_2_2.save()

		atom_2_1_1 = Atom(trail_segment=trail_seg_2, coordinates="0.0,1.0 0.25,0.75", parcel=parcel, \
			segment_id=0, position_id=0)
		atom_2_1_1.save()

		atom_2_1_2 = Atom(trail_segment=trail_seg_2, coordinates="0.25,0.75 0.75,0.25", parcel=parcel, \
			segment_id=0, position_id=1)
		atom_2_1_2.save()

		atom_2_1_3 = Atom(trail_segment=trail_seg_2, coordinates="0.75,0.25 1.0,0.0", parcel=parcel, \
			segment_id=0, position_id=2)
		atom_2_1_3.save()

		# Perform test
		placemarks = DBManager.retrievePlacemarkData()
		self.assertEqual(len(placemarks), 2)
		self.assertEqual(placemarks[0].name, "Trail 1")
		self.assertEqual(placemarks[1].name, "Trail 2")
		self.assertEqual(len(placemarks[0].line_segments), 2)
		self.assertEqual(len(placemarks[0].line_segments[0].coordinates), 2)
		self.assertEqual(len(placemarks[0].line_segments[1].coordinates), 3)
		self.assertEqual(len(placemarks[1].line_segments), 1)
		self.assertEqual(len(placemarks[1].line_segments[0].coordinates), 4)

	def test_saveTrailData_multiple_placemarks(self):
		""" Test saving multiple trail placemarks into the database """
		# Create test objects
		# ... Parcel 1
		parcel_1 = LocationObjects.Parcel('123', "Owner", "city", address="123 Fake Ln, Charlottesville, 12345", distance_to_trail=500, notes="Need permission",permissions="www.abc.com")
		parcel_1.addPoints([(-7.0, -7.0), (-7.0, 7.0), (7.0, 7.0), (7.0, -7.0)], 0)

		# ... Placemark 1
		placemark_1 = LocationObjects.Placemark("Trail 1", "Description...", status="Open", styleUrl="")

		placemark_1_segment_1_line_1 = LocationObjects.LineSegment()
		placemark_1_segment_1_line_1.coordinates = [LocationObjects.Coordinate(0.0, 0.0, 0.0), LocationObjects.Coordinate(1.0, 1.0, 0.0)]
		placemark_1_segment_1_line_2 = LocationObjects.LineSegment()
		placemark_1_segment_1_line_2.coordinates = [LocationObjects.Coordinate(1.0, 1.0, 0.0), LocationObjects.Coordinate(2.0, 2.0, 0.0)]
		placemark_1_segment_1 = [placemark_1_segment_1_line_1, placemark_1_segment_1_line_2]

		placemark_1_segment_2_line_1 = LocationObjects.LineSegment()
		placemark_1_segment_2_line_1.coordinates = [LocationObjects.Coordinate(2.0, 2.0, 0.0), LocationObjects.Coordinate(3.0, 3.0, 0.0)]
		placemark_1_segment_2 = [placemark_1_segment_2_line_1]

		placemark_1_segments = [placemark_1_segment_1, placemark_1_segment_2]
		placemark_1.generateAtoms(placemark_1_segments)
		for atom in placemark_1.atoms:
			atom.setParcel(parcel_1)

		# ... Placemark 2
		placemark_2 = LocationObjects.Placemark("Trail 2", "Description...", status="Open", styleUrl="")

		placemark_2_segment_1_line_1 = LocationObjects.LineSegment()
		placemark_2_segment_1_line_1.coordinates = [LocationObjects.Coordinate(0.0, 0.0, 0.0), LocationObjects.Coordinate(-1.0, -1.0, 0.0)]
		placemark_2_segment_1_line_2 = LocationObjects.LineSegment()
		placemark_2_segment_1_line_2.coordinates = [LocationObjects.Coordinate(-1.0, -1.0, 0.0), LocationObjects.Coordinate(-2.0, -2.0, 0.0)]
		placemark_2_segment_1 = [placemark_2_segment_1_line_1, placemark_2_segment_1_line_2]

		placemark_2_segments = [placemark_2_segment_1]
		placemark_2.generateAtoms(placemark_2_segments)
		# .... No associated parcels
		for atom in placemark_2.atoms:
			atom.setParcel(None)

		# ... Collect all placemarks
		placemarks = [placemark_1, placemark_2]

		# Perform test
		DBManager.saveTrailData(placemarks)

		# ... Trails
		trail_segments = TrailSegment.objects.all()
		self.assertEqual(len(trail_segments), 2)
		self.assertEqual(len(Atom.objects.all()), 5)

		# ... Trail 1
		self.assertEqual(trail_segments[0].name, "Trail 1")
		# ... ... Segment 1
		trail_1_segment_1_atoms = Atom.objects.filter(trail_segment=trail_segments[0], segment_id=0)
		self.assertEqual(len(trail_1_segment_1_atoms), 2)
		# ... ... Segment 2
		trail_1_segment_2_atoms = Atom.objects.filter(trail_segment=trail_segments[0], segment_id=1)
		self.assertEqual(len(trail_1_segment_2_atoms), 1)

		# ... Trail 2
		self.assertEqual(trail_segments[1].name, "Trail 2")
		# ... ... Segment 1
		trail_2_segment_1_atoms = Atom.objects.filter(trail_segment=trail_segments[1], segment_id=0)
		self.assertEqual(len(trail_2_segment_1_atoms), 2)

		# ... Parcels
		self.assertEqual(len(Parcel.objects.all()), 1)

	def test_create_new_user(self):
		""" Test creating a new user in the system """
		# Create test objects
		user_form = UserForm(data={"username": "username", "password": "password", "email": "admin@email.com"})
		user_saved = user_form.save()

		# Perform test
		DBManager.create_new_user(user_saved)
		self.assertEqual(len(User.objects.all()), 1)
		self.assertEqual(len(User.objects.filter(username='username')), 1)
		user = User.objects.filter(username='username').first()
		self.assertEqual(user.email, 'admin@email.com')

	def test_create_maintenance_request_fail(self):
		""" Test the failing case of creating a maintenance request """
		# Perform test
		self.assertEqual(DBManager.create_maintenance_request(None, None, None), False)
		self.assertEqual(DBManager.create_maintenance_request(None, None, True), False)
		self.assertEqual(DBManager.create_maintenance_request(None, True, None), False)
		self.assertEqual(DBManager.create_maintenance_request(None, True, True), False)
		self.assertEqual(DBManager.create_maintenance_request(True, None, None), False)
		self.assertEqual(DBManager.create_maintenance_request(True, None, True), False)
		self.assertEqual(DBManager.create_maintenance_request(True, True, None), False)

	def test_get_maintenance_requests_single_request(self):
		""" Test retrieving a single Maintenance Request stored """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		requests = DBManager.get_maintenance_requests()
		self.assertEqual(len(requests), 2)
		self.assertEqual(sum([(request.description == "Test Description 1" and request.pk == 0) for request in requests]), 1)
		self.assertEqual(sum([(request.description == "Test Description 2" and request.pk == 1) for request in requests]), 1)

	def test_get_maintenance_requests_no_requests(self):
		""" Test retrieving when there are no requests """
		# Create test objects
		# ... None
		# Perform test
		requests = DBManager.get_maintenance_requests()
		self.assertEqual(len(requests), 0)

	def test_get_maintenance_requests_with_id(self):
		""" Test retrieving a request via id """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		self.assertEqual(type(request), MaintenanceRequest)
		self.assertEqual(request.description, "Test Description 2")
		self.assertEqual(request.location, "23.4545,-54.32123")
		self.assertEqual(request.created_by, "User2")
		self.assertEqual(request.resolved, False)

	def test_get_maintenance_requests_with_id_doesnt_exist(self):
		""" Test retrieving a request via id when no such request exists """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=2)
		self.assertEqual(request, None)

	def test_create_maintenace_request_single_request(self):
		""" Test creating a maintenance request """
		# Create test objects
		DBManager.create_maintenance_request(description="Unique Description", location="72.34,-122.3", user="User3")
		# Perform test
		request = MaintenanceRequest.objects.get(description="Unique Description")
		self.assertEqual(request.description, "Unique Description")
		self.assertEqual(request.location, "72.34,-122.3")
		self.assertEqual(request.created_by, "User3")
		self.assertEqual(request.resolved, False)

	def test_get_maintenance_requests_with_filter(self):
		""" Test retrieving when there is a filter """
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		filters = {'description': "Test Description 1"}
		requests = DBManager.get_maintenance_requests(request_filters=filters)
		self.assertEqual(len(requests), 1)

	def test_get_maintenance_requests_with_bad_filter(self):
		""" Test retrieving when there is a non standard filter"""		
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		filters = {'apple': "2"}
		requests = DBManager.get_maintenance_requests(request_filters=filters)
		self.assertEqual(len(requests), 2)

	def test_convert_unicode_boolean(self):
		""" Test conversion of string to boolean"""	
		true_string = 'True'
		not_true_string = 'Anything'
		self.assertTrue(DBManager.convert_unicode_boolean(true_string))
		self.assertFalse(DBManager.convert_unicode_boolean(not_true_string))

	def test_parse_mr_filters_with_mixed(self):
		""" Test parsing of filters for a dict of allowed and not allowed filters"""
		mixed_filters = {'description': 'test', 'resolved': 'true', 'apples': 'bad'}
		parsed = DBManager.parse_mr_filters(mixed_filters)
		self.assertEqual(parsed, {'description': 'test', 'resolved': True})


	def test_parse_mr_filters_only_bad(self):
		""" Test parsing of filters for a dict only not allowed filters-should be None"""		
		bad_filters = {'apples': 1, 'bananas': 2, 'oranges': 3}
		parsed = DBManager.parse_mr_filters(bad_filters)
		self.assertEqual(parsed, None)

	def test_edit_maintenance_request(self):
		""" Test editing a single Maintenance Request stored """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		test_desc = "New Test Description 2"
		DBManager.edit_maintenance_request(1, description=test_desc)	
		request = DBManager.get_maintenance_requests(m_id=1)
		self.assertEqual(request.description, "New Test Description 2")		

	def test_edit_maintenance_request_no_request(self):
		""" Test editing a single Maintenance Request that does not exist """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		ret = DBManager.edit_maintenance_request(4)
		self.assertEqual(ret, False)

	def test_edit_maintenance_request_resolved(self):
		""" Test resolving a maintenance request """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		DBManager.edit_maintenance_request(1, resolved=True)
		request = DBManager.get_maintenance_requests(m_id=1)
		self.assertEqual(request.resolved, True)
		self.assertNotEqual(request.resolved_timestamp, None)

	def test_edit_maintenance_request_unresolved(self):
		""" Test unresolving a maintenance request """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", resolved=True, created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		DBManager.edit_maintenance_request(1, resolved=False)
		request = DBManager.get_maintenance_requests(m_id=1)
		self.assertEqual(request.resolved, False)
		self.assertEqual(request.resolved_timestamp, None)

	def test_edit_maintenance_request_no_edits(self):
		""" Test that if no edits to object were made, the object won't be changed """
		# Create test objects
		MaintenanceRequest.objects.create(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		MaintenanceRequest.objects.create(pk=1, description="Test Description 2", location="23.4545,-54.32123", created_by="User2")
		# Perform test
		request = DBManager.get_maintenance_requests(m_id=1)
		DBManager.edit_maintenance_request(1)
		request = DBManager.get_maintenance_requests(m_id=1)
		self.assertEqual(request.description, "Test Description 2")
		self.assertEqual(request.location, "23.4545,-54.32123")
		self.assertEqual(request.created_by, "User2")

	def test_edit_maintenance_request_user(self):
		""" Test that an edit can change the user """
		# Create test objects
		mr = MaintenanceRequest(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		mr.save()
		# Perform test
		DBManager.edit_maintenance_request(0, user="User2")
		edited_request = MaintenanceRequest.objects.filter(pk=0).first()
		self.assertEqual(edited_request.created_by, "User2")

	def test_edit_maintenance_request_location(self):
		""" Test that an edit can change the location """
		# Create test objects
		mr = MaintenanceRequest(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		mr.save()
		# Perform test
		DBManager.edit_maintenance_request(0, location="0.0,0.0")
		edited_request = MaintenanceRequest.objects.filter(pk=0).first()
		self.assertEqual(edited_request.location, "0.0,0.0")

	def test_delete_maintenance_request_valid_request(self):
		""" Test deleting a valid maintenance request """
		# Create test objects
		mr = MaintenanceRequest(pk=0, description="Test Description 1", location="23.45,-54.321", created_by="User1")
		mr.save()
		# Perform test
		self.assertEqual(DBManager.delete_maintenance_request(0), True)
		self.assertEqual(len(MaintenanceRequest.objects.filter(pk=0)), 0)

	def test_delete_maintenance_request_invalid_request(self):
		""" Test deleting an invalid maintenance request """
		# Create test objects
		# ... None
		# Perform test
		self.assertEqual(DBManager.delete_maintenance_request(0), False)
		self.assertEqual(len(MaintenanceRequest.objects.filter(pk=0)), 0)

	def test_create_new_user_profile(self):
		""" Test creating a new user profile associated with a user """
		# Create test objects
		user_form = UserForm(data={"username": "username", "password": "password", "email": "admin@email.com"})
		user_saved = user_form.save()
		DBManager.create_new_user(user_saved)
		user_profile_form = UserProfileForm(data={"phone_number": '123456789012345'})

		# Perform test
		user_profile_saved = user_profile_form.save(commit=False)
		DBManager.create_new_user_profile(user_profile_saved, user_saved)

		self.assertEqual(len(UserProfile.objects.all()), 1)
		self.assertEqual(len(UserProfile.objects.filter(user=User.objects.filter(username="username").first())), 1)
		user_profile = UserProfile.objects.filter(user=User.objects.filter(username="username").first()).first()
		self.assertEqual(user_profile.phone_number, '123456789012345')

	def test_create_intersection_task(self):
		""" Test creating an Intersection Task object in the database """
		# Create test objects
		task_id = DBManager.create_intersection_task(1337)

		# Perform test
		intersection = IntersectionTask.objects.filter(pk=task_id).first()
		self.assertEqual(intersection.placemarks, 1337)
		self.assertEqual(intersection.placemarks_completed, 0)
		self.assertEqual(intersection.parcels_extracted, False)

	def test_edit_intersection_task_invalid_task(self):
		""" Test editing an invalid Intersection Task object """
		# Create test objects
		# ... None
		# Perform test
		self.assertEqual(DBManager.edit_intersection_task(0, parcels_extracted=True), False)

	def test_edit_intersection_task_all_fields_but_averaging(self):
		""" Test editing an Intersection Task with all the relevant fields """
		# Create test objects
		intersection = IntersectionTask(pk=0, placemarks=1, placemarks_completed=0, parcels_extracted=False)
		intersection.save()
		time_elapsed = timedelta(seconds=1)
		timestamp = datetime.now()

		# Perform test
		self.assertEqual(DBManager.edit_intersection_task(0, parcels_extracted=True, placemark_time=time_elapsed, \
			placemarks_completed=1, finished=timestamp), \
			True)
		intersection_db = IntersectionTask.objects.filter(pk=0).first()
		self.assertEqual(intersection_db.parcels_extracted, True)
		self.assertEqual(intersection_db.placemark_avg_time, time_elapsed)
		self.assertEqual(intersection_db.placemarks_completed, 1)
		self.assertNotEqual(intersection_db.finished, None)

	def test_edit_intersection_task_averaging(self):
		""" Test editing averaging time for an Intersection Task """
		# Create test objects
		intersection = IntersectionTask(pk=0, placemarks=3, placemarks_completed=0, parcels_extracted=False)
		intersection.save()
		time_elapsed_1 = timedelta(seconds=1)
		time_elapsed_2 = timedelta(seconds=2)
		time_elapsed_3 = timedelta(seconds=3)
		time_elapsed_list = [time_elapsed_1, time_elapsed_2, time_elapsed_3]
		expected_avg_time = reduce(lambda x, y: x + y, time_elapsed_list) / len(time_elapsed_list)
		timestamp = datetime.now()

		# Perform test
		self.assertEqual(DBManager.edit_intersection_task(0, parcels_extracted=True, placemark_time=time_elapsed_1, placemarks_completed=1), \
			True)
		self.assertEqual(DBManager.edit_intersection_task(0, placemark_time=time_elapsed_2, placemarks_completed=2), \
			True)
		self.assertEqual(DBManager.edit_intersection_task(0, placemark_time=time_elapsed_3, placemarks_completed=3, finished=timestamp), \
			True)
		intersection_db = IntersectionTask.objects.filter(pk=0).first()
		self.assertEqual(intersection_db.parcels_extracted, True)
		self.assertEqual(intersection_db.placemark_avg_time, expected_avg_time)
		self.assertEqual(intersection_db.placemarks_completed, 3)
		self.assertNotEqual(intersection_db.finished, None)

	def test_get_running_intersection_task_first_from_desc_order(self):
		""" Test retrieving running Intersection Task objects in descending start order """
		# Create test objects
		first_time = datetime.now() - timedelta(seconds=10)
		second_time = datetime.now() - timedelta(seconds=5)

		intersection_1 = IntersectionTask(pk=0, placemarks_completed=0, placemarks=3, started=first_time)
		intersection_1.save()
		intersection_2 = IntersectionTask(pk=1, placemarks_completed=0, placemarks=5, started=second_time)
		intersection_2.save()

		# Perform test
		running_intersection = DBManager.get_running_intersection_task()
		self.assertEqual(running_intersection.pk, 1)
		self.assertEqual(running_intersection.placemarks, 5)

	def test_get_running_intersection_task_all_finished(self):
		""" Test retrieving running Intersection Task objects in descending start order """
		# Create test objects
		intersection_1 = IntersectionTask(pk=0, placemarks=3, placemarks_completed=3, parcels_extracted=True, finished=datetime.now())
		intersection_1.save()
		intersection_2 = IntersectionTask(pk=1, placemarks=5, placemarks_completed=5, parcels_extracted=True, finished=datetime.now())
		intersection_2.save()

		# Perform test
		self.assertEqual(DBManager.get_running_intersection_task(), None)

	def test_save_parcels_new_parcel(self):
		parcel_new = LocationObjects.Parcel('2', "Owner", "city", address="123 Fake Ln, Charlottesville, 12345", distance_to_trail=500)
		parcel_new.addPoints([(-7.0, -7.0), (-7.0, 7.0), (7.0, 7.0), (7.0, -7.0)], 0)
		parcels = [parcel_new]
		DBManager.save_parcels(parcels)
		p_test = Parcel.objects.filter(pid=2, parcel_type='city').first() 
		self.assertEqual(p_test.owner, 'Owner')
		self.assertEqual(p_test.address, '123 Fake Ln, Charlottesville, 12345')

	def test_save_parcels_edit_parcel(self):
		parcel_old = Parcel(pid='1', size=1.234, \
			owner="Owner", address="123 Fake Ln", on_trail=True, \
			points_string="0.0,0.0 0.0,1.0 1.0,1.0 1.0,0.0", parcel_type="city", \
			distance_to_trail=500, notes="", permissions="")
		parcel_old.save()
		p_test = Parcel.objects.filter(pid=1, parcel_type='city').first() 
		self.assertEqual(p_test.owner, 'Owner')
		self.assertEqual(p_test.address, '123 Fake Ln')
		parcel_old = LocationObjects.Parcel('1', "Owner", "city", address="123 Fake Ln, Charlottesville, 12345", distance_to_trail=500)
		parcel_old.addPoints([(-7.0, -7.0), (-7.0, 7.0), (7.0, 7.0), (7.0, -7.0)], 0)
		parcels = [parcel_old]
		DBManager.save_parcels(parcels)
		p_test = Parcel.objects.filter(pid=1, parcel_type='city').first() 
		self.assertEqual(p_test.owner, 'Owner')
		self.assertEqual(p_test.address, '123 Fake Ln, Charlottesville, 12345')

