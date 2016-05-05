# Manager system for interacting with database


from django.apps import apps
from rtfapp.models import TrailSegment, Parcel, Atom, MaintenanceRequest, IntersectionTask
from LocationObjects import Placemark, Coordinate, LineSegment
from LocationObjects import Atom as LocationObjectsAtom
import datetime
from django.utils import timezone

def deleteTrailData():
	""" Delete all placemarks, parcels, and atoms from database """

	# print "Deleting TrailSegments, Parcels, and Atoms from Database!"

	TrailSegment.objects.all().delete()
	Parcel.objects.all().delete()
	Atom.objects.all().delete()

def retrievePlacemarkData():
	""" Retrieve all placemarks with atoms for storing to KML """

	# print "Retrieving TrailSegments and Atoms to Construct KML"

	placemarks = []
	trail_segs = TrailSegment.objects.all()

	for trail in trail_segs:
		placemark = Placemark(trail.name, trail.description, status=trail.trail_status, current_conditions=trail.current_conditions, \
			styleUrl=trail.style_url, pk=trail.id)
		
		segment = 0
		atom_set = Atom.objects.filter(trail_segment=trail, segment_id=segment).order_by('position_id')
		while len(atom_set) > 0:
			current_line_segment = LineSegment()

			# Parse first coordinates
			atom = atom_set[0]
			locAtom = LocationObjectsAtom(linestring=None, placemark=placemark)
			locAtom.parseCoordinates(atom.coordinates)
			start_point = locAtom.coordinates.coords[0]
			current_line_segment.coordinates.append(Coordinate(start_point[0], start_point[1], 0))

			# Parse atom coordinates
			for atom in atom_set:
				locAtom = LocationObjectsAtom(linestring=None, placemark=placemark)
				locAtom.parseCoordinates(atom.coordinates)
				end_point = locAtom.coordinates.coords[1]
				current_line_segment.coordinates.append(Coordinate(end_point[0], end_point[1], 0))

			# Append line segmnet
			placemark.line_segments.append(current_line_segment)

			# Next iteration
			segment += 1
			atom_set = Atom.objects.filter(trail_segment=trail, segment_id=segment).order_by('position_id')

		# Add to placemarks
		placemarks.append(placemark)

	return placemarks

def saveTrailData(placemarks):
	""" Store placemarks, parcels, and atoms """

	# print "Storing TrailSegments, Parcels, and Atoms to Database."

	trail_count = 0
	parcel_count = 0
	atom_count = 0

	for pm in placemarks:
		# Store placemark as a TrailSegment
		trail_seg = TrailSegment(name=pm.name, description=pm.description, trail_status=pm.status, style_url=pm.styleUrl)
		trail_seg.save()
		trail_count += 1

		for atom in pm.atoms:
			cp = atom.parcel
			if cp:
				parcel = Parcel.objects.filter(pid=cp.id, parcel_type=cp.p_type).first()
			else:
				parcel = None

			# Store Parcel (if it doesn't already exist in the db)
			if cp and not parcel:
				parcel = Parcel(pid=cp.id, size=cp.getSize(), \
					owner=cp.owner, address=cp.address, on_trail=cp.on_trail, \
					points_string=cp.formatCoordinates(), parcel_type=cp.p_type, \
					distance_to_trail = cp.distance_to_trail, notes=cp.notes, permissions=cp.permissions)
				parcel.save()
				parcel_count += 1

			# Store Atom
			db_atom = Atom(trail_segment=trail_seg, coordinates=atom.formatCoordinates(), parcel=parcel, \
				segment_id=atom.segment, position_id=atom.position)
			db_atom.save()
			atom_count += 1

	# print "Trails (%d), Parcels (%d), Atoms (%d)" % (trail_count, parcel_count, atom_count, )

def edit_trail(id, status, description, name, current_conditions):
	trail = TrailSegment.objects.filter(pk=id).first()
	if trail == None:
		return False
	trail.trail_status = status
	trail.description = description
	trail.name = name
	trail.current_conditions = current_conditions
	trail.style_url = '#line-00FF00-3' if trail.trail_status == 'Open' else '#line-FF0000-3'
	trail.last_edit = datetime.datetime.now()
	trail.save()
	return True

def edit_parcel(id, owner, permissions, notes, address, parcel_type):
	#print "Edit parcel function reached, id (%s) owner (%s) permissions (%s)" % (id, owner, permissions)
	parcel = Parcel.objects.filter(pk=id).first()
	if parcel == None:
		return False
	parcel.owner = owner
	parcel.permissions = permissions
	parcel.notes = notes
	parcel.address = address
	parcel.parcel_type = parcel_type
	parcel.save()
	return True

def save_parcels(parcels):
	for cp in parcels:
		parcel = Parcel.objects.filter(pid=cp.id, parcel_type=cp.p_type).first()
		if not parcel:
			# make a new parcel
			parcel = Parcel(pid=cp.id, size=cp.getSize(), \
						owner=cp.owner, address=cp.address, on_trail=cp.on_trail, \
						points_string=cp.formatCoordinates(), parcel_type=cp.p_type, \
						distance_to_trail=cp.distance_to_trail, notes=cp.notes, permissions=cp.permissions)
		else:
			# parcel exists, update fields
			parcel.size = cp.getSize()
			parcel.owner = cp.owner
			parcel.permissions = cp.permissions
			parcel.notes = cp.notes
			parcel.address = cp.address
			parcel.on_trail = cp.on_trail
			parcel.points_string = cp.formatCoordinates()
			parcel.distance_to_trail = cp.distance_to_trail


		parcel.save()


def create_new_user(newuser):
	#Save a new user from the registration form
	newuser.set_password(newuser.password)
	newuser.is_superuser = True
	newuser.is_staff = True
	newuser.save()

def create_maintenance_request(description, location, user):
	if not description or not location or not user:
		return False
	m = MaintenanceRequest(description=description, location=location, created_by=user)
	m.save()
	return True

def convert_unicode_boolean(val):
	"""Returns true if val is a string that is True or true else false"""
	return val == u'true' or val == u'True'

def parse_mr_filters(request_filters):
	"""Removes all non allowed filters from the filter list"""
	filters = {}
	if request_filters:	
		allowable_filters = {'description':'text', 'location':'text', 'created_by':'text', 'resolved':'boolean'}		
		for f in request_filters:			
			if f in allowable_filters:
				filters[f] = convert_unicode_boolean(request_filters[f]) if allowable_filters[f] == 'boolean' else request_filters[f]
	return filters if len(filters) > 0 else None

def get_maintenance_requests(m_id = None, request_filters = None):

	""" Gets a list of MaitenanceRequests from the database 
		Can get single request if m_id is specified
		Can filter requests based on filters object """
	if m_id:
		return MaintenanceRequest.objects.filter(id=m_id).first()

	m_requests = MaintenanceRequest.objects.all()	

	filters = parse_mr_filters(request_filters)
	if filters:
		m_requests = m_requests.filter(**filters)
	return m_requests

def edit_maintenance_request(m_id, resolved=False, description=None, location=None, user=None):
	m = MaintenanceRequest.objects.filter(id=m_id).first()

	if not m:
		return False

	if user:
		m.created_by = user

	if description:
		m.description = description

	if location:
		m.location = location

	m.resolved = resolved

	if resolved:
		m.resolved_timestamp = timezone.now()
	else:
		m.resolved_timestamp = None
		
	m.save()
	return True

def delete_maintenance_request(m_id):
	m = MaintenanceRequest.objects.filter(id=m_id).first()

	if not m:
		return False

	m.delete()
	return True

def create_new_user_profile(newuser_profile, newuser):
	#Create a new user profile and link it to the newly created user
	newuser_profile.user = newuser
	newuser_profile.email = newuser.email
	newuser_profile.password_hash = newuser.password
	newuser_profile.save()

def create_intersection_task(num_placemarks):
	""" Create an object to store intersection task information 
		Returns the id of the newly created task 
	"""
	task = IntersectionTask(placemarks=num_placemarks, placemarks_completed=0, parcels_extracted=False)
	task.save()
	return task.id

def edit_intersection_task(task_id, parcels_extracted=None, placemark_time=None, placemarks_completed=None, finished=None):
	""" Edit an intersection task in the database """
	task = IntersectionTask.objects.filter(id=task_id).first()
	if not task:
		return False

	# Parcels done extracting
	if parcels_extracted:
		task.parcels_extracted = True

	# Do the averaging first
	if placemark_time and task.placemarks_completed == 0:
		task.placemark_avg_time = placemark_time
	elif placemark_time:
		task.placemark_avg_time = ((task.placemark_avg_time * task.placemarks_completed) + placemark_time) / (task.placemarks_completed + 1)

	# Adjust completed placemarks
	if placemarks_completed is not None and int(placemarks_completed) > 0:
		task.placemarks_completed = int(placemarks_completed)

	# Finished the task
	if finished:
		task.finished = datetime.datetime.now()

	task.save()
	return True

def get_running_intersection_task():
	""" Get the currently running intersection task object or None """
	return IntersectionTask.objects.filter(finished=None).order_by('-started').first()

# DB dump functions
def get_model_list():
	#get a list of all models
	this_app = apps.get_app_config('rtfapp')
	model_list = this_app.models.values()
	return model_list

def dump_model(model):
	return model.objects.all()
