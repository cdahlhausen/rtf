from django.db import models
from django.contrib.auth.models import User



class TrailSegment(models.Model):
	""" Trail Segment including line segments on trail """
	STATUS_CHOICES = [
		('Open', 'Open'),
		('Closed', 'Closed')
	]

	description = models.TextField()
	difficulty = models.IntegerField(default=0)
	name = models.TextField()
	last_edit = models.DateTimeField(auto_now_add=True)
	trail_status = models.CharField(choices=STATUS_CHOICES, default='Open', max_length=10)
	current_conditions = models.TextField()
	style_url = models.TextField()

class MaintenanceRequest(models.Model):
	""" Maintenance Request """
	description = models.TextField()
	submit_timestamp = models.DateTimeField(auto_now_add=True)
	resolved_timestamp = models.DateTimeField(blank=True, null=True)
	resolved = models.BooleanField(default=False)
	# optional One-to-one relationship with User
	# head_user = models.OneToOneField(User, unique=False, blank=True, null=True)
	created_by = models.TextField()
	# optional Many-to-many relationship with TrailSegment
	location = models.TextField()

class ParcelStatus(models.Model):
    """ Parcel status with coloration and label """
    label = models.CharField(max_length=255)
    color = models.CharField(max_length=7) # hex value

    def to_json(self):
    	return {
    		'label': self.label,
    		'color': self.color,
    		'id': self.id
    	}


def get_default_status():
	""" get default status for parcels """
	try: 
		status = ParcelStatus.objects.get(id=1)
	except DoesNotExist:
		status = ParcelStatus(label="Uncategorized", color="#00aaee")
	return status


# todo: add agreement status (will color on map) and ADDRESS
class Parcel(models.Model):
	""" Parcel for legal documentation """
	# Property identified - from city/county data
	pid = models.CharField(max_length=16)
	# Size of parcel, needs more specific unit like sq. meters
	size = models.DecimalField(max_digits=10, decimal_places=5, default=0.0)
	# Who owns the property
	owner = models.TextField()
	# Style: "lat,long lat,long ..."
	points_string = models.TextField()
	# Usually a city or a county
	parcel_type = models.CharField(max_length=255)
	# Legal status of the parcel (used on front end of the map to filter properties)
	# status = models.CharField(max_length=255, default=None)
	# Address of parcel
	address = models.TextField(default=None)
	# Whether or not the parcel is crossed by the trail
	on_trail = models.BooleanField(default=False)
	# distance to nearest trail segment
	distance_to_trail = models.FloatField()
	# Link to permissions documents on Google Drive
	permissions = models.CharField(max_length=255, default=None)
	# Miscellaneous Notes
	notes = models.CharField(max_length=255, default=None)
	status = models.ForeignKey(ParcelStatus, default=get_default_status)
	# color for parcel, overwrites status.color
	color = models.CharField(max_length=7, default='', blank=True)

class Atom(models.Model):
	""" Atoms: contained line segments that compose trail segments """
	# Style: "lat,long lat,long ..."
	coordinates = models.TextField()
	# Many-to-one relationship with Parcel
	parcel = models.ForeignKey(Parcel, blank=True, null=True)
	# Many-to-one relationship with TrailSegment
	trail_segment = models.ForeignKey(TrailSegment)
	last_edit = models.DateTimeField(auto_now_add=True)
	# Segment and position within Trail Segment that this atom belong to
	segment_id = models.IntegerField()
	position_id = models.IntegerField()

class Permission(models.Model):
	""" Permission documents for a given parcel"""
	parcel = models.ForeignKey(Parcel)
	last_edit = models.DateTimeField(auto_now_add=True)
	expiration_date = models.DateTimeField()
	path_to_doc = models.TextField()
	summary = models.TextField()

class UserProfile(models.Model):
	""" Additional information to store with a user """
	user = models.OneToOneField(User, primary_key=True)
	phone_number = models.CharField(max_length=15)
	email = models.CharField(max_length=255, blank=True, null =True)
	password_hash = models.CharField(max_length=512, blank=True, null=True)
	forgot_password_hash = models.CharField(max_length=512, blank=True, null=True)

class IntersectionTask(models.Model):
	""" Stored progress for a trail-parcel intersection task """
	started = models.DateTimeField(auto_now_add=True)
	finished = models.DateTimeField(blank=True, null=True)
	placemarks = models.IntegerField()
	placemarks_completed = models.IntegerField()
	placemark_avg_time = models.DurationField(null=True)
	parcels_extracted = models.BooleanField(default=False)
