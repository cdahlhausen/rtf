$(document).ready(function() {
	$("#descriptionFilter").on("input", function() {
		onFilterChange('description');
	}).trigger("input");
	$("#created_byFilter").on("input", function() {
		onFilterChange('created_by')
	}).trigger("input");
});

var currentLocation = undefined,
	zoomedIn = false,
	prioritizeMaintenaceRequestClicks = false;

function setFormFieldLocation(lat, lng) {
	document.getElementById('createMaintenanceRequestLatitude').value = lat;
	document.getElementById('createMaintenanceRequestLongitude').value = lng;

	// Round two decimal places
	lat = Math.round(lat * 100) / 100;
	lng = Math.round(lng * 100) / 100;

	document.getElementById('createMaintenanceRequestLatitudeDisplay').innerHTML = lat;
	document.getElementById('createMaintenanceRequestLongitudeDisplay').innerHTML = lng;
}
function setLocation(position) {
	setFormFieldLocation(position.coords.latitude, position.coords.longitude);
	addCurrentLocationToMap({lat: position.coords.latitude, lng: position.coords.longitude}, true);
}
function getLocation() {
    if (navigator.geolocation && typeof(navigator.geolocation.getCurrentPosition) === "function") {
        navigator.geolocation.getCurrentPosition(setLocation);
    } else {
        alert("Cannot access device location, please select a location on the map.");
    }
}
function areMaintenanceRequestClicksPrioritized() {
	return prioritizeMaintenaceRequestClicks;
}
function getCurrentLocation() {
	return currentLocation;
}
function setCurrentLocation(marker) {
	currentLocation = marker;
}
function allowMaintenanceRequestMapClick() {
	// Remove previous marker
	if (currentLocation !== undefined && currentLocation != null) {
		currentLocation.setMap(null);
		currentLocation = null;
	}



	alert("Go ahead, click the map.");

	// Clear previous click listeners on the map
	google.maps.event.clearListeners(map, 'click');

	// Inform other listeners to report to our event
	prioritizeMaintenaceRequestClicks = true;

	// Add listener
	map.addListener('click', maintenanceRequestClicked);
}
var isZoomedIn = function () {
	return zoomedIn;
};
var setZoomedIn = function (z) {
	zoomedIn = z;
};
var maintenanceRequestClicked = function (e) {
	// Clear click listener
	google.maps.event.clearListeners(map, 'click');

	// Set form fields
	setFormFieldLocation(e.latLng.lat(), e.latLng.lng());

	// Add location to map
	addCurrentLocationToMap(e.latLng, !zoomedIn);

	// Tell other listeners to stop reporting to our event
	prioritizeMaintenaceRequestClicks = false;
};
function removeCurrentLocationFromMap() {
	if (currentLocation !== undefined && currentLocation != null) {
		currentLocation.setMap(null);
		currentLocation = null;
	}

	// Catch all, reset priority for maintenance requests to override click events
	prioritizeMaintenaceRequestClicks = false;
}
function addCurrentLocationToMap(location, pan) {
	removeCurrentLocationFromMap();

	currentLocation = new google.maps.Marker({
        position: location,
        title: 'New Maintenance Request',
        draggable: true, 
        map: map
    });

    // Add drag listener
    currentLocation.addListener("dragend", doneDraggingMarker);

    if (pan) {
    	map.panTo(location);
    }

    map.setZoom(16);
    zoomedIn = true;
}
var doneDraggingMarker = function (e) {
	// Set form fields
	setFormFieldLocation(e.latLng.lat(), e.latLng.lng());
};


var mRequests = [],
	openRequest = -1,
	filters = {
		'created_by': '',
		'resolved': false,
		'description': ''
	},
	mRequestsOnMap = [];

var parseLatLng = function (str) {
	if (str === undefined || str === null) {
		return null;
	}

	var matches = str.match(/([+-])?\d+(\.\d+)?/g)
	if (matches === undefined || matches === null || matches.length != 2) {
		return null;
	}

	return {
		lat: parseFloat(matches[0]),
		lng: parseFloat(matches[1])
	};
};

var clearRequestsOnMap = function () {
	// No requests on map
	if (mRequestsOnMap === undefined || mRequestsOnMap == null || mRequestsOnMap.length == 0) {
		return;
	}

	// Clear each request from map
	mRequestsOnMap.forEach(function (request) {
		if (request !== undefined && request != null && request.marker != null) {
			request.marker.setMap(null);
			request.marker = null;
			request = null;
		}
	});

	// Empty array
	mRequestsOnMap = [];
};
var getMaintenanceRequestsOnMap = function () {
	return mRequestsOnMap;
};
var setMaintenanceRequestsOnMap = function (requests) {
	mRequestsOnMap = requests;
};
var addRequestToMap = function (request) {
	// Create marker
	mapRequest = {
		marker: new google.maps.Marker({
	        position: 	parseLatLng(request["fields"]["location"]),
	        title: 		"#" + request["pk"].toString(),
	        icon: 		request["fields"]["resolved"] ? "http://maps.google.com/mapfiles/ms/icons/green-dot.png" : "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
	        animation: 	google.maps.Animation.DROP,
	        map: 		map,
	    }),
	    id: request["pk"]
	};

	// Create tooltip
	var tooltipHtml = "<h4>#" + request["pk"].toString() + " - " + (request["fields"]["resolved"] ? "Closed" : "Open") + "</h4>" +
					  "<hr />" + 
					  "<h5>" + request["fields"]["description"] + "</h5>" + 
					  "<h5>Created by: <b>" + request["fields"]["created_by"] + "</b></h5>" + 
					  "<h5>Created on: <i>" + Date(request["fields"]["submit_timestamp"]) + "</i></h5>" + 
					  "<hr />" +
					  "<h5>" + 
					  	"<button type='button' class='btn btn-primary' onclick='editSpecificRequest(" + request["pk"] + ")'>Edit</button>" + 
					  	(!request["fields"]["resolved"] ? " <button type='button' class='btn btn-success' onclick='resolveSpecificRequest(" + request["pk"] + ")'>Resolve</button>" : "") + 
					  "</h5>";
	attachMaintenanceRequestTooltip(mapRequest, tooltipHtml, map);

	// Click to zoom
	mapRequest.marker.addListener("click", function () {
		zoomToRequest(request["pk"]);
	});

    // Add to array
    mRequestsOnMap.push(mapRequest);
};

function attachMaintenanceRequestTooltip(currentRequest, html, map) {
	// Create info window to store with object that holds marker
	currentRequest.infoWindow = new google.maps.InfoWindow({
		content: html,
	});

	// Click to display tooltip
	google.maps.event.addListener(currentRequest.marker, 'click', function(e) {
		// Adjust by a bit to be slightly above marker
		var adjustedLatLng = new google.maps.LatLng({lat: e.latLng.lat() + 0.0005, lng: e.latLng.lng()});
		this.setOptions({fillOpacity:0.1});
		currentRequest.infoWindow.setPosition(adjustedLatLng);
		currentRequest.infoWindow.open(map);
	});
}

var hideMaintenanceRequestInfoWindows = function () {
	// Hide tooltips that may be open for maintenance requests
	mRequestsOnMap.forEach(function (request) {
		request.infoWindow.close();
	});
};

var zoomToRequest = function (pk) {
	// Exit if no requests on map
	if (mRequestsOnMap === undefined || mRequestsOnMap == null || mRequestsOnMap.length == 0) {
		return;
	}

	// Find request by id
	var request = null;
	for (var i = 0; i < mRequestsOnMap.length; i++) {
		if (mRequestsOnMap[i].id == pk) {
			request = mRequestsOnMap[i];
			break;
		}
	}

	// Couldn't find
	if (request == null) {
		return;
	}

	// Pan to location
	map.panTo(request.marker.position);

    // Zoom
    map.setZoom(16);
	zoomedIn = true;
};

var getRequests = function(showRequests) {
	var filters = {};
	showRequests = typeof(showRequests) === "boolean" && showRequests;

	$.ajax({
		url: "../rtfapp/maintenance-requests/",
		type: "GET",
		data: filters,
		success: function(json) {
			mRequests = json;
			var htmlString = "";

			// Clear map
			clearRequestsOnMap();

			// Hide other screens, show requests
			if (showRequests !== undefined && showRequests) {
				if (typeof(hideOtherViews) === "function") {
					hideOtherViews();
				}
				$("#createMaintenanceRequest").hide();
				$("#editMaintenanceRequest").hide();
				$("#maintenanceRequests").show();
			}

			if(mRequests.length > 0) {
				if (showRequests) {
					$("#noRequests").hide();
				}

				mRequests.forEach(function(r) {

					// Add location
					var locParsed = parseLatLng(r["fields"]["location"]);
					r["fields"]["latitude"] = locParsed.lat;
					r["fields"]["longitude"] = locParsed.lng;

					htmlString += "<div class=\"m-request\" id=\"mRequest" + r["pk"] + "\">Maintenance Request " + r["pk"] + ":<br><ul>";
					htmlString += "<li>Status: " + (r["fields"]["resolved"] ? "Closed" : "Open") + "</li>";
					htmlString += "<li>Submitted: " + Date(r["fields"]["submit_timestamp"]) + "</li>";
					htmlString += "<li>Created by: " + r["fields"]["created_by"] + "</li>";
					htmlString += "<li>Location: " + r["fields"]["location"] + "</li>";
					htmlString += "<li>Description: " + r["fields"]["description"] + "</li>";
					htmlString += "</ul></div>";

					// Add to map
					addRequestToMap(r);
				});
			} else {
				if (showRequests) {
					$("#noRequests").show();
				}
			}

			$("#requestList").html(htmlString);
			$('.m-request').click(maintenanceRequestDivClicked);
		},
		error: function(xhr, errmsg, err) {
			console.log("ERROR:" + errmsg);
		}
	});
};
var setMaintenanceRequests = function (maintenanceRequests) {
	mRequests = maintenanceRequests;
};
var maintenanceRequestDivClicked = function() {
	if($(this).hasClass('selected')) {
		openRequest = -1;
	} else {
		if(openRequest !== -1) { $('#mRequest'+openRequest).removeClass('selected'); }						
		openRequest = Number($(this).attr('id').substr(8));						
	}
	$(this).toggleClass('selected');
};
var getOpenRequest = function () {
	return openRequest;
};
var setOpenRequest = function (r) {
	openRequest = r;
};
var editSpecificRequest = function(requestNum) {
	openRequest = requestNum;
	hideMaintenanceRequestInfoWindows();
	showEditRequest(true);
};
var showEditRequest = function(open) {
	var formList = [
		['description',"textarea[name=editMaintenanceRequestDescription]"], 
		['created_by',"input[name=editMaintenanceRequestUser]"]
	];

	if(open && openRequest >= 0) {
		// Get request with id
		var currentRequest = getRequestWithId(openRequest);
		// Set description and created_by
		formList.forEach(function (item) {
			$(item[1]).val(currentRequest['fields'][item[0]]);
		});
		// Set location
		currentRequestLocation = parseLatLng(currentRequest["fields"]["location"]);
		$("span#editMaintenanceRequestLatitude").html(currentRequestLocation.lat);
		$("span#editMaintenanceRequestLongitude").html(currentRequestLocation.lng);
		
		if (currentRequest["fields"]["resolved"]) {
			$("select[name=editMaintenanceRequestResolved]").val("true");
		} else {
			$("select[name=editMaintenanceRequestResolved]").val("false");
		}
		// Hide other screens, show edit request
		if (typeof(hideOtherViews) === "function") {
			hideOtherViews();
		}
		
		$("#createMaintenanceRequest").hide();
		$("#maintenanceRequests").hide();
		$("#editMaintenanceRequest").show();
	} else {
		formList.forEach(function (item) {
			if (item[0] !== "resolved") {
				$(item[1]).val("");
			}
		});
		// Hide other screens, show all requests
		if (typeof(hideOtherViews) === "function") {
			hideOtherViews();
		}

		$("#createMaintenanceRequest").hide();
		$("#editMaintenanceRequest").hide();
		$("#maintenanceRequests").show();
	}
};
var editRequest = function() {
	var formList = [
		"textarea[name=editMaintenanceRequestDescription]", 
		"input[name=editMaintenanceRequestUser]",
		"select[name=editMaintenanceRequestResolved]"
	];

	var formValid = true;
	formList.forEach(function (item) {
		if ($(item).val() === "") {
			formValid = false;
			$(item).css("background-color", "#ff5151");
		} else {
			$(item).css("background-color", "#ffffff");
		}
	});

	if (!formValid) {
		return;
	}

	var formData = {
		'description': $("textarea[name=editMaintenanceRequestDescription]").val(),
		'user': $("input[name=editMaintenanceRequestUser]").val(),
		'latitude': $("span#editMaintenanceRequestLatitude").html(),
		'longitude': $("span#editMaintenanceRequestLongitude").html(),
		'resolved': ($("select[name=editMaintenanceRequestResolved]").val() === "true")
	};

	$.ajax({
		url: "../rtfapp/maintenance-requests/" + openRequest + "/",
		type: "POST",
		data: formData,
		success: function(json) {
			getRequests(true);
		},
		error: function(xhr, errmsg, err) {
			console.log("ERROR:" + errmsg);
		}
	});
};
var showCreateRequest = function(open) {
	// Remove info from boxes
	var formList = [
		"textarea[name=createMaintenanceRequestDescription]", 
		"input[name=createMaintenanceRequestUser]", 
		"input[name=createMaintenanceRequestLatitude]", 
		"input[name=createMaintenanceRequestLongitude]"
	];
	formList.forEach(function(item){
		$(item).val("");
	});

	// Clear location displays
	$("span#createMaintenanceRequestLatitude").html("NaN");
	$("span#createMaintenanceRequestLongitude").html("NaN");

	// Remove Marker
	removeCurrentLocationFromMap();

	if(open) {
		// Hide other screens, show create request
		if (typeof(hideOtherViews) === "function") {
			hideOtherViews();
		}

		$("#maintenanceRequests").hide();
		$("#editMaintenanceRequest").hide();
		$("#createMaintenanceRequest").show();
	} else {
		// Hide other screens, show all requests
		if (typeof(hideOtherViews) === "function") {
			hideOtherViews();
		}

		$("#editMaintenanceRequest").hide();
		$("#createMaintenanceRequest").hide();
		$("#maintenanceRequests").show();
	}
};
var createRequest = function() {
	var formList = [
		"textarea[name=createMaintenanceRequestDescription]", 
		"input[name=createMaintenanceRequestUser]", 
		"input[name=createMaintenanceRequestLatitude]", 
		"input[name=createMaintenanceRequestLongitude]"
	];
	var formValid = true;

	formList.forEach(function (item) {
		if ($(item).val() === "") {
			formValid = false;
			$(item).css("background-color", "#ff5151");
		} else {
			$(item).css("background-color", "#fff");
		}
	});

	if (!formValid) {
		return;
	}

	var formData = {
		'description': $("textarea[name=createMaintenanceRequestDescription]").val(),
		'user': $("input[name=createMaintenanceRequestUser]").val(),
		'latitude': $("input[name=createMaintenanceRequestLatitude]").val(),
		'longitude': $("input[name=createMaintenanceRequestLongitude]").val()
	};

	$.ajax({
		type: 'POST',
		url: '../rtfapp/maintenance-requests/',
		data: formData,
		success: function(data) {
			if (data.success) {
				$("#mobilerequestMessage").css("display", "block");
				$("#mobilerequestMap").css("display", "none");
				
				$("#mrequestMessage").css("display", "block");
				setTimeout(function() {
					$("#mrequestMessage").css("display", "none");
				}, 5000);
			}
			removeCurrentLocationFromMap();
			formList.forEach(function(item) {
				$(item).val("");
				$(item).css("background-color", "#fff");
			});

			// Get them again
			getRequests(true);
		},
		error: function(xhr, error) {
			console.log("ERROR:" + error);
		}
	});
};
var resolveSpecificRequest = function (requestNum) {
	openRequest = requestNum;
	hideMaintenanceRequestInfoWindows();
	resolveRequest();
};
var resolveRequest = function() {
	var formData = {
		'resolved': true
	};

	$.ajax({
		url: "../rtfapp/maintenance-requests/" + openRequest + "/",
		type: "POST",
		data: formData,
		success: function(json) {
			getRequests(true);
		},
		error: function(xhr, errmsg, err) {
			console.log("ERROR:" + errmsg);
		}
	});
};
var deleteRequest = function() {
	$.ajax({
		url: "../rtfapp/maintenance-requests/" + openRequest + "/",
		type: "DELETE",
		success: function(json) {
			getRequests(true);
		},
		error: function(xhr, errmsg, err) {
			console.log("ERROR:" + errmsg);
		}
	});
};
var getRequestWithId = function(id) {
	for(var i = 0; i < mRequests.length; i++) {
		if(mRequests[i]["pk"] === id) {
			return mRequests[i];
		}
	}
	return -1;
};
var getFilterValue = function (filter) {
	return filters[filter];
};
var resetFilters = function () {
	filters = {
		'created_by': '',
		'resolved': 'false',
		'description': ''
	};
	Object.keys(filters).forEach(function (filter) {
		$("#" + filter + "Filter").val(filters[filter]);
	});
};
var onFilterChange = function(filter) {
	var newVal = $('#'+filter + 'Filter').val();
	if(filters[filter] !== newVal) {
		// console.log("MY VALUE HAS CHANGED");
		filters[filter] = newVal;
		applyFilters();
	}		
};
var applyFilters = function() {		
	var toShow, toShowCount = 0;
	mRequests.forEach(function(request) {
		toShow = true;
		if(filters['created_by'] !== '' && toShow) {
			toShow = request["fields"]["created_by"].indexOf(filters['created_by']) > -1;
		}
		if(filters['description'] !== '' && toShow) {
			toShow = request["fields"]["description"].indexOf(filters['description']) > -1;
		}
		if(filters['resolved'] !== '' && toShow) {
			toShow = request["fields"]["resolved"] == (filters['resolved'] === "true");
		}
		if(toShow) {
			$('#mRequest'+request["pk"]).show();
			toShowCount++;
		} else {
			if(openRequest === request["pk"]) {
				$('#mRequest'+request["pk"]).removeClass('selected');
				openRequest = -1;
			}
			$('#mRequest'+request["pk"]).hide();				
		}
	});
	if(toShowCount === 0) {
		$("#noRequests").show();
	} else {
		$("#noRequests").hide();			
	}
};
var clearFilters = function() {
	resetFilters();
	applyFilters();
};