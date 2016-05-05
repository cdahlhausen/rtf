from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q


from .models import User, UserProfile, TrailSegment, Atom, IntersectionTask
from .forms import UserForm, UserEditForm, UserProfileForm, TrailAnnotationForm
from .tasks import intersect_task

from .models import User, UserProfile, TrailSegment, Parcel, ParcelStatus

from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.core import serializers
from .managers import FileSystemManager, KMZManager, SHPManager, DBManager, LocationObjects
import time, datetime, os, mimetypes, csv, json, re, djqscsv

from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse, HttpResponseForbidden

from rtfapp.models import get_default_status

# Timestamp (month-day-year_hour-minutes-seconds)
timestamp_format = "%m-%d-%Y_%H-%M-%S"


def index(request):
	if request.user.is_authenticated():
		response = administration(request)
		return HttpResponseRedirect("administration/")
	else:
		return render(request, 'rtfapp/index.html')

def submit_request(request):
	return render(request, 'rtfapp/submit_request.html')

@login_required
def administration(request):  
  templateFile = 'rtfapp/administration.html'
  context = RequestContext(request)
  parcels = json.dumps(serialize_parcels(Parcel.objects.filter(on_trail=True)))
  return render_to_response(templateFile, {'parcels': parcels}, context)

  
@login_required
def register(request):
	'''Register a new user'''
	context = RequestContext(request)
	errors = ""
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		user_profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and user_profile_form.is_valid():
			newuser = user_form.save()
			DBManager.create_new_user(newuser)
			newuser_profile = user_profile_form.save(commit=False)
			DBManager.create_new_user_profile(newuser_profile, newuser)
			return render_to_response('rtfapp/administration.html', {'name': newuser.username}, context)

		else:
			errors = user_form.errors
			prof_form_errors = user_profile_form.errors
			return render_to_response('rtfapp/register.html', {'user_form': user_form, 'user_profile_form': user_profile_form,
													   'errors': errors, 'up_form_errors': prof_form_errors}, context)
	else:
		#get
		user_form = UserForm()
		user_profile_form = UserProfileForm()
	return render_to_response('rtfapp/register.html', {'user_form': user_form, 'user_profile_form': user_profile_form,
													   }, context)

@login_required
def edit_profile(request):
	'''Edit this user's profile'''
	context = RequestContext(request)
	curr_user = request.user
	curr_user_profile = None
	try:
		curr_user_profile = UserProfile.objects.get(user=curr_user.id)
	except ObjectDoesNotExist:
		#create profile on the fly
		newuser_profile = UserProfile()
		newuser_profile.user = request.user
		newuser_profile.email = request.user.email
		newuser_profile.password_hash = request.user.password
		newuser_profile.save()
		curr_user_profile = newuser_profile
	if request.method == 'POST':
		user_edit_form = UserEditForm(data=request.POST, instance=curr_user)
		user_profile_edit_form = UserProfileForm(data=request.POST, instance=curr_user_profile)
		if user_edit_form.is_valid() and user_profile_edit_form.is_valid():
			#I feel very dirty doing this this way, but as far as I can tell there isn't an easier/better way?
			new_username = request.POST.get("username")
			if new_username != curr_user.username:
				curr_user.username = new_username
			phone_number = request.POST.get("phone_number")
			if phone_number != curr_user_profile.phone_number:
				curr_user_profile.phone_number = phone_number
			new_email = request.POST.get("email")
			if curr_user.email != new_email:
				curr_user.email = new_email
				curr_user_profile.email = new_email
			curr_user.save()
			curr_user_profile.save()
		return render_to_response('rtfapp/administration.html', {'edit_name': curr_user.username}, context)



	else:
		user_edit_form = UserEditForm(instance=curr_user)
		user_profile_edit_form = UserProfileForm(instance=curr_user_profile)
	return render_to_response('rtfapp/edit_profile.html', {'user_form': user_edit_form, 'user_profile_form': user_profile_edit_form}, context)


def downloadKMZ(request):
	""" Download the KMZ file with database content """
	kmzDir = FileSystemManager.fromHomeDir("kmz/")

	# Retrieve kmzFiles
	kmzFilePath = FileSystemManager.findLatestFile(kmzDir, ".kmz", timestamp_format)

	# Check for errors in file paths
	errors = []

	if kmzFilePath is None:
		errors.append("Unable to retrieve KMZ file, this must be uploaded")

	# Don't proceed if there are errors
	if errors:
		return HttpResponse(json.dumps({"errors": errors}))

	# Extract KML files, which saves to server file system
	kmlFiles = KMZManager.extractKMLFiles(kmzFilePath, kmzDir)
	kmlDoc = KMZManager.constructKMLFromPlacemarks(DBManager.retrievePlacemarkData(), kmlFiles[0])

	# Save file and zip
	outputDir = FileSystemManager.fromHomeDir("kmz-downloads/")
	kmlFile = FileSystemManager.fromDir(outputDir, "doc.kml")
	kmzFile = "rivanna_trail.kmz"
	kmzFilePath = FileSystemManager.fromDir(outputDir, kmzFile)

	FileSystemManager.saveFile(kmlFile, kmlDoc.to_string(prettyprint=True).encode("utf8"), overwrite=True)
	FileSystemManager.zip([kmlFile], kmzFile, output_dir=outputDir, overwrite=True)

	chunk_size = 8192
	response = StreamingHttpResponse(FileWrapper(open(kmzFilePath), chunk_size),
			content_type=mimetypes.guess_type(kmzFilePath)[0])
	response["Content-Length"] = os.path.getsize(kmzFilePath)
	response["Content-Disposition"] = 'attachment; filename=%s' % kmzFile
	return response

@login_required
def downloadDB(request):
	""" Download database contents as a zipped folder of CSVs
	"""
	#magically get a list of all models
	models = DBManager.get_model_list()
	home_dir = FileSystemManager.getHomeDir()
	file_list = []

	for model in models:
		if model._meta.verbose_name == "intersection task":
			#it doesn't make sense to dump these
			continue
		#get all objects for this model
		queryset = DBManager.dump_model(model)
		#write 1 csv per model, temporarily to homedir
		with open(home_dir + "/" + model._meta.verbose_name+".csv", "wb") as file:
			djqscsv.write_csv(queryset, file, use_verbose_names=False)
			file_list.append(file.name)
			file.close()

	#make sure there isn't an old copy of this file laying around
	if os.path.exists(home_dir + "/db.zip"):
		os.remove(home_dir + "/db.zip")

	#create zip
	FileSystemManager.zip(file_list, "db.zip")

	#wrap up and respond
	with open(home_dir +"/db.zip") as file:
		wrapper = FileWrapper(file)
		response = HttpResponse(wrapper)
		response['Content-Type'] = "application/zip"
		response['Content-Disposition'] = 'attachment; filename=db.zip'
		#clean up
		for file in file_list:
			os.remove(file)
		return response

def uploadDB(request):
	templateFile = 'rtfapp/uploadDBfromCSV.html'

	# Check for form submission
	if request.method == "POST" and "dbFile" in request.FILES:
		#Save zip file to home
		dbFile = request.FILES["dbFile"]
		dbFilePath = FileSystemManager.fromHomeDir("db.zip")
		FileSystemManager.saveFile(dbFilePath,
			dbFile.read(), overwrite=True)
		#unzip
		home = FileSystemManager.getHomeDir()
		file_list = FileSystemManager.unzip(dbFilePath)
		model_list = DBManager.get_model_list()
		#clean up file list (remove paths/extensions)
		csv_list = []
		for file in file_list:
			csv_list.append(file.split("/")[-1])
		#csv_list is a list of the names of every csv file in the zip
		#they should match the model's verbose name
		for csvf in csv_list:
			model_name = csvf.split(".")[0]
			for model in model_list:
				#go through every csv, match to an rtf_app model (NOT auth models)
				if model_name == model._meta.verbose_name:
					with open(home+"/"+csvf, 'r') as currfile:
						my_reader = csv.DictReader(currfile)
						for row in my_reader:
							newobj = model()
							for field in my_reader.fieldnames:
								for key in row.keys():
									#kludge for the fact that djqscsv writes as unicode, screwing up key-values
									#as far as the csv module is concerned
									if '\ufeff' in key:
										new_key = key.lstrip('\ufeff')
										field = new_key
										row[new_key] = row.pop(key)
									if '\xbf' in key:
										new_key = key.replace('\xef\xbb\xbf', '')
										field = new_key
										row[new_key] = row.pop(key)
								#may clean this up later
								setattr(newobj, field, row[field])
							newobj.save()
		return HttpResponse("Database upload successful<br><a href=\"/administration\">Return home </a>")

		# Default to form for upload
	return render(request, templateFile, {})

def maintenance_requests(request, pk=None):
	""" RESTful access to maintenance requests """
	if request.method == "POST" and (pk is None):
		if(all(x in request.POST for x in ['description', 'user', 'latitude', 'longitude'])):
			location = LocationObjects.formatCoordinateString([(float(request.POST['latitude']), float(request.POST['longitude']))])
			success = DBManager.create_maintenance_request(request.POST['description'], location, request.POST['user'])
		else:
			success = False
		data = json.dumps({"success": success})
		return HttpResponse(data, content_type="application/json")
	elif request.method == "GET":
		allowable_filters = {'description':'text', 'location':'text', 'created_by':'text', 'resolved':'boolean'}
		filters = {}
		for f in request.GET:
			if f in allowable_filters:
				filters[f] = convertUnicodeBoolean(request.GET[f]) if allowable_filters[f] == 'boolean' else request.GET[f]
		mrequests = DBManager.get_maintenance_requests(request_filters=filters)	
		data = serializers.serialize('json', mrequests)
		return HttpResponse(data, content_type="application/json")
	elif request.method == "POST" and pk:
		if(all(x in request.POST for x in ['description', 'user', 'latitude', 'longitude', 'resolved'])):
			# Edit
			location = LocationObjects.formatCoordinateString([(float(request.POST['latitude']), float(request.POST['longitude']))])
			success = DBManager.edit_maintenance_request(m_id=pk, resolved=convertUnicodeBoolean(request.POST['resolved']), \
				description=request.POST['description'], location=location, user=request.POST['user'])
		elif "resolved" in request.POST:
			success = DBManager.edit_maintenance_request(m_id=pk, resolved=request.POST['resolved'])
		else:
			success = False
		return HttpResponse(json.dumps({"success": success}), content_type="application/json")
	elif request.method == "DELETE" and pk:
		success = DBManager.delete_maintenance_request(pk)
		data = json.dumps({"success": success})
		return HttpResponse(data, content_type="application/json")

def placemarks(request):
	""" RESTful access to maintenance requests """
	if request.method == "POST":
		#Cannot at this time create a new trail segment
		#Instead used to EDIT current trail segement
		if(all([x in request.POST for x in ['id', 'status', 'description', 'name', 'current_conditions']])):
			result = DBManager.edit_trail(request.POST['id'],request.POST['status'], request.POST['description'],request.POST['name'],request.POST['current_conditions'])
			data = json.dumps({"success": result})
		else:		
			data = json.dumps({"success": False, "message": "Invalid edit request. More data is required"})			
		return HttpResponse(data, content_type="application/json")
	elif request.method == "GET":
		pm_dict = serialize_placemarks(DBManager.retrievePlacemarkData())
  		pms = json.dumps(pm_dict)
		return HttpResponse(pms, content_type="application/json")	
	elif request.method == "DELETE":
		#Cannot delete trail segments		
		return HttpResponse(json.dumps({"success": False, "message": "Cannot delete trail through this request"}), 
			content_type="application/json")

def serialize_placemarks(placemarks):
  new_dict = {"placemarks": []}
  for pm in placemarks:
    pm_dict = {"lines": [map(lambda x: {"lat": x.latitude, "lng": x.longitude}, ls.coordinates) for ls in pm.line_segments]}
    pm_dict['name'] = pm.name
    pm_dict["description"] = pm.description
    pm_dict["status"] = pm.status
    pm_dict["conditions"] = pm.current_conditions
    pm_dict["id"] = pm.id
    # Parse style color and size
    hexRE = "[0-9,A-F]"
    colors = re.findall("".join([hexRE for x in range(6)]), pm.styleUrl)
    pm_dict["styleColor"] = "#" + (colors[0] if len(colors) > 0 else "FF0000")
    pm_dict["styleSize"] = 5
    new_dict["placemarks"].append(pm_dict)
  return new_dict

@login_required
def queue_intersection(request):
	""" RESTful access to queueing a trail-parcel intersection """	
	if request.method == "POST" and any(x in request.FILES for x in ['pointFiles', 'areaFiles', 'kmzFile', 'countyShpFiles', 'countyExcelFiles']):
		# Save files or retrieve latest
		# ---------------------------------------------------

		timestamp = datetime.datetime.fromtimestamp(time.time()).strftime(timestamp_format)

		# Storage directories for content (from home dir)
		cityPointsDir = FileSystemManager.fromHomeDir("cityPoints/")
		cityAreasDir = FileSystemManager.fromHomeDir("cityAreas/")
		kmzDir = FileSystemManager.fromHomeDir("kmz/")
		countyAreasDir = FileSystemManager.fromHomeDir("countyAreas/")
		countyExcelDir = FileSystemManager.fromHomeDir("countyExcel/")
		files_given = {"cityPoint": False, "cityArea": False, "kmz": False, "countyArea": False, "countyExcel": False}

		# Retrieve pointFiles or get latest
		if "pointFiles" in request.FILES:
			cityPointZip = request.FILES["pointFiles"]
			cityPointFilePath = cityPointsDir + timestamp + ".zip"
			files_given["cityPoint"] = True
		else:
			cityPointZip = None
			cityPointFilePath = FileSystemManager.findLatestFile(cityPointsDir, ".zip", timestamp_format)

		# Retrieve areaFiles or get latest
		if "areaFiles" in request.FILES:
			cityAreaZip = request.FILES["areaFiles"]
			areaFilePath = cityAreasDir + timestamp + ".zip"
			files_given["cityArea"] = True
		else:
			cityAreaZip = None
			areaFilePath = FileSystemManager.findLatestFile(cityAreasDir, ".zip", timestamp_format)

		# Retrieve kmzFiles or get latest
		if "kmzFile" in request.FILES:
			kmlZip = request.FILES["kmzFile"]
			kmzFilePath = kmzDir + timestamp + ".kmz"
			files_given["kmz"] = True
		else:
			kmlZip = None
			kmzFilePath = FileSystemManager.findLatestFile(kmzDir, ".kmz", timestamp_format)

		# Retrieve countyAreaFiles or get latest
		if "countyShpFiles" in request.FILES:
			countyAreaZip = request.FILES["countyShpFiles"]
			countyAreaFilePath = countyAreasDir + timestamp + ".zip"
			files_given["countyArea"] = True
		else:
			countyAreaZip = None
			countyAreaFilePath = FileSystemManager.findLatestFile(countyAreasDir, ".zip", timestamp_format)

		# Retrieve countyExcelFiles or get latest
		if "countyExcelFiles" in request.FILES:
			countyExcelZip = request.FILES["countyExcelFiles"]
			countyExcelFilePath = countyExcelDir + timestamp + ".zip"
			files_given["countyExcel"] = True
		else:
			countyExcelZip = None
			countyExcelFilePath = FileSystemManager.findLatestFile(countyExcelDir, ".zip", timestamp_format)

		# Check for errors in file paths
		errors = []

		if cityPointZip is None and cityPointFilePath is None:
			errors.append("Unable to retrieve Point zip file, this must be uploaded")

		if cityAreaZip is None and areaFilePath is None:
			errors.append("Unable to retrieve Area zip file, this must be uploaded")

		if kmlZip is None and kmzFilePath is None:
			errors.append("Unable to retrieve KMZ file, this must be uploaded")

		if countyAreaZip is None and countyAreaFilePath is None:
			errors.append("Unable to retrieve County Area zip file, this must be uploaded")

		if countyExcelZip is None and countyExcelFilePath is None:
			errors.append("Unable to retrieve County Excel zip file, this must be uploaded")

		# Don't proceed if there are errors
		if errors:
			return HttpResponse(json.dumps({"errors": errors, "taskId": -1}), content_type="application/json")

		# Extract zip files uploaded
		if cityPointZip and files_given["cityPoint"]:
			FileSystemManager.saveFile(cityPointFilePath, cityPointZip.read(), overwrite=True)

		if cityAreaZip and files_given["cityArea"]:
			FileSystemManager.saveFile(areaFilePath, cityAreaZip.read(), overwrite=True)

		if kmlZip and files_given["kmz"]:
			FileSystemManager.saveFile(kmzFilePath, kmlZip.read(), overwrite=True)

		if countyAreaZip and files_given["countyArea"]:
			FileSystemManager.saveFile(countyAreaFilePath, countyAreaZip.read(), overwrite=True)

		if countyExcelZip and files_given["countyExcel"]:
			FileSystemManager.saveFile(countyExcelFilePath, countyExcelZip.read(), overwrite=True)

		# Get number of placemarks to store in Intersection Task in database
		kmz_dir = FileSystemManager.fromHomeDir("kmz/")	
		kml_files = KMZManager.extractKMLFiles(kmzFilePath, kmz_dir)		
		placemarks = KMZManager.getKMLPlacemarks(kml_files)
		num_marks = len(placemarks)

		# Create intersection task in database
		task_id = DBManager.create_intersection_task(num_marks)
		# Queue an intersection process
		intersect_task.delay(task_id, kmzFilePath, cityPointFilePath, areaFilePath, countyAreaFilePath, countyExcelFilePath)
		# Return task model information
		return HttpResponse(json.dumps({"taskId": task_id}), content_type="application/json")

	elif request.method == "GET":
		# Retrieve task progress for latest intersection
		task = DBManager.get_running_intersection_task()
		# print task
		if task:
			return HttpResponse(json.dumps({"taskId": task.id, "parcelsExtracted": task.parcels_extracted, \
				"placemarksCompleted": task.placemarks_completed, "placemarks": task.placemarks, "started": str(task.started), \
				"placemarkAvgTime": task.placemark_avg_time.seconds if task.placemark_avg_time else None}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({"taskId": -1}), content_type="application/json")
	else:
		return HttpResponse(json.dumps({"taskId": -1}), content_type="application/json")

def convertUnicodeBoolean(val):
	return val == u'true' or val == u'True'

# restful endpoint for parcels
# todo: implement other http verbs if necessary
def parcels(request):
	# just do get request, return all parcels
	data = "must do get"
	if request.method == "POST":
		#Cannot at this time create a new parcel
		#Instead used to EDIT current parcel
		if(all([x in request.POST for x in ['id', 'owner', 'permissions', 'notes', 'address', 'type']])):
			result = DBManager.edit_parcel(request.POST['id'],request.POST['owner'],request.POST['permissions'],request.POST['notes'],request.POST['address'],request.POST['type'])
			parcel = Parcel.objects.get(id=request.POST['id'])
			parcel.status = ParcelStatus.objects.get(id=request.POST['status'])
			parcel.save()
			data = json.dumps({"success": result})
		else:		
			data = json.dumps({"success": False, "message": "Invalid edit request. More data is required"})			
		return HttpResponse(data, content_type="application/json")

	if request.method == 'GET':

		if 'filter' in request.GET:
			filter_type = request.GET['filter']
			if filter_type == 'onTrail':
				parcels = Parcel.objects.filter(on_trail=True)
			elif filter_type == 'within':
				within = float(request.GET['within'])
				parcels = Parcel.objects.filter(distance_to_trail__lte=within)
			else:
				parcels = Parcel.objects.all()
		else:
			parcels = Parcel.objects.all()
		
		data = json.dumps(serialize_parcels(parcels))

	return HttpResponse(data, content_type="application/json")


# convert set of parcels for json serialization
def serialize_parcels(parcels):
	result = []
	for parcel in parcels:
		new_parcel = {}
		new_parcel["id"] = parcel.pk
		new_parcel["points"] = map(lambda x: {"lat": x.split(",")[0], "lng":x.split(",")[1]}, parcel.points_string.split(" "))
		new_parcel["owner"] = parcel.owner
		new_parcel["address"] = parcel.address
		new_parcel["type"] = parcel.parcel_type.upper()
		new_parcel["permissions"] = parcel.permissions
		new_parcel["notes"] = parcel.notes
		new_parcel["status"] = parcel.status.to_json()
		result.append(new_parcel)

	return result

def parcel_statuses(request, pk=None):
	data = ''
	if request.method == 'POST':
		if pk:
			status = get_object_or_404(ParcelStatus, pk=pk)
			status.label = request.POST['label']
			status.color = request.POST['color']
			status.save()
		else:
			# save new status
			status = ParcelStatus(label=request.POST['label'], color=request.POST['color'])
			status.save()
		data = json.dumps(status.to_json())
		
	elif request.method == 'GET':
		if pk:
			status = get_object_or_404(ParcelStatus, pk=pk)
			data = json.dumps(status.to_json())
		else:
			data = json.dumps([status.to_json() for status in ParcelStatus.objects.all()])

	elif request.method == 'DELETE' and pk:
		
		if pk == 1:
			# gets hung here, won't respond
			return HttpResponseForbidden()

		status = get_object_or_404(ParcelStatus, pk=pk)
		parcels = Parcel.objects.filter(status__id=pk)
		for parcel in parcels:
			parcel.status = get_default_status()
			parcel.save()
		status.delete()
		return HttpResponse(status=204)
	
	return HttpResponse(data, content_type='application/json')
