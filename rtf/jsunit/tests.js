/**
 * Additional test functions
 */
var epsilonValue = 0.00001,
	assertDoubleCloseEnough = function (expected, actual) {
		return Math.abs(expected - actual) <= epsilonValue;
	};

var ucharToHex = function (i) {
		// i in [0, 255]
		i = Math.max(0, i) % 256;

		var output = i.toString(16).toUpperCase(),
			additional = (i < 16) ? "0" : "";

		return additional + output;
	},
	rgbStrToHex = function (str) {
		var matches = str.match(/([+-])?\d+/g);
		if (matches === undefined || matches === null || matches.length < 3) {
			return null;
		}

		var hexValues = [0, 1, 2].map(function (index) { return ucharToHex(parseInt(matches[index])); });
		return hexValues.reduce(function (pv, cv) { return pv + cv; }, "#");
	};

var getCSSByName = function (name, prop) {
		var names = document.getElementsByName(name);

		if (names.length <= 0) {
			return null;
		}

		return names[0].style.getPropertyValue(prop);
	},
	setCSSById = function (id, prop, value) {
		var elem = document.getElementById(id);

		if (elem === undefined || elem === null) {
			return false;
		}

		elem.style[prop] = value;
		return elem.style[prop] === value;
	};

/**
 * Mock functions
 */
var map,
	mapPanToCounter = 0,
	mockMapPanTo = function (l) {
		mapPanToCounter++;
	},
	mapListeners = {},
	mockMapAddListener = function (type, callback) {
		if (!(type in mapListeners) || mapListeners[type] === undefined || mapListeners[type] === null) {
			mapListeners[type] = [];
		}

		mapListeners[type].push(callback);
	},
	mockMapClearListeners = function (googleMap, type) {
		mapListeners[type] = undefined;
	},
	mockMapMarker = function (forMap, lat, lng, title, draggable) {
		return new google.maps.Marker({
	        position: {lat: (lat !== undefined) ? lat : 0.0, lng: (lng !== undefined) ? lng : 0.0},
	        title: (title !== undefined) ? title : "Marker",
	        draggable: (draggable !== undefined) ? draggable : false, 
	        map: (forMap !== undefined) ? forMap : map
	    });
	},
	mockMap = function (mapOptions) {
		// Default map options
		if (mapOptions === undefined) {
			mapOptions = {
				zoom: 13,
				center: new google.maps.LatLng(0.0, 0.0),
				mapTypeId: google.maps.MapTypeId.HYBRID
			};
		}

		// Set global
	    map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

	    // Fake panTo
	    mapPanToCounter = 0;
	    map.panTo = mockMapPanTo;

	    // Fake addListeners
	    mapListeners = {};
	    map.addListener = mockMapAddListener;

	    // Fake clearListeners
	    if (google.maps.event === undefined) {
	    	google.maps.event = {};
	    }

	    google.maps.event.clearListeners = mockMapClearListeners;

	    return map;
	};

var mockFakeLocationEvent = function (lat, lng) {
	return {
		latLng: new google.maps.LatLng((lat !== undefined) ? lat : 0.0, (lng !== undefined) ? lng : 0.0)
	};
};

var mockMaintenanceRequest = function (fromMap, pk, lat, lng, resolved) {
	return {
		marker: new google.maps.Marker({
	        position: 	{lat: (lat !== undefined) ? lat : 0.0, lng: (lng !== undefined) ? lng : 0.0},
	        title: 		"#" + ((pk !== undefined) ? pk : -1),
	        icon: 		(typeof(resolved) === "boolean" && resolved) ? "http://maps.google.com/mapfiles/ms/icons/green-dot.png" : "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
	        animation: 	google.maps.Animation.DROP,
	        map: 		(fromMap !== undefined) ? fromMap : map
	    }),
	    id: (pk !== undefined) ? pk : -1
	};
};

var mockMaintenanceRequestFromServer = function (pk, location, resolved, description, createdBy, submitTimestamp) {
	return {
		pk: (pk !== undefined) ? pk : -1,
		fields: {
			location: (location !== undefined) ? location : "0.0,0.0",
			resolved: (typeof(resolved) === "boolean") ? resolved : false,
			description: (description !== undefined) ? description : "",
			created_by: (createdBy !== undefined) ? createdBy : "",
			submit_timestamp: (submitTimestamp !== undefined) ? submitTimestamp : ""
		}
	};
};

var hideOtherViewsCount = 0,
	mockHideOtherViews = function () {
		hideOtherViewsCount = 0;
		hideOtherViews = function () {
			hideOtherViewsCount++;
		};
	};

var infoWindowCloseCount = 0,
	mockInfoWindowClose = function () {
		infoWindowCloseCount++;
	},
	infoWindowOpenCount = 0,
	mockInfoWindowOpen = function () {
		infoWindowOpenCount++;
	},
	mockInfoWindow = function (content) {
		var infoWindow = new google.maps.InfoWindow({ content: content });

		// Override open
		infoWindow.open = mockInfoWindowOpen;

		// Override close
		infoWindow.close = mockInfoWindowClose;

		return infoWindow;
	},
	resetMockInfoWindowCounts = function () {
		infoWindowOpenCount = 0;
		infoWindowCloseCount = 0;
	};

var mockGeolocation = function (on, lat, lng) {
	var hasLatLng = (lat !== undefined && lng !== undefined),
		tempMockLocation =  {
			coords: {
				latitude: (hasLatLng) ? lat : 0.0,
				longitude: (hasLatLng) ? lng: 0.0
			}
		};

	// May have to generate objects for phantomjs
	if (window.navigator === undefined) {
		window.navigator = {};
	}

	if (window.navigator.geolocation === undefined) {
		window.navigator.geolocation = {};
	}
	
	// Turn on mock functionality
	if (on) {
		window.navigator.geolocation.getCurrentPosition = function (callback) { callback(tempMockLocation); };
	} else {
		window.navigator.geolocation.getCurrentPosition = undefined;
	}
};

var timeouts = [],
	mockTimeouts = function () {
		timeouts = [];
		window.setTimeout = function (f, t) {
			timeouts.push({ fcn: f, time: t });
		};
	};

var alertCount = 0,
	mockWindowAlert = function () {
		alertCount = 0;
		window.alert = function (message) {
			alertCount++;
		};
	};

var mockAjaxGETRequests = {},
	mockAjaxPOSTRequests = {},
	mockAjaxDELETERequests = {},
	mockAjaxCall = function () {
		// Reset request objects
		mockAjaxGETRequests = {};
		mockAjaxPOSTRequests = {};
		mockAjaxDELETERequests = {};

		// Override ajax call
		$.ajax = function (request) {
			if (request.type === "GET") {
				mockAjaxGETRequests[request.url] = request;
			} else if (request.type === "POST") {
				mockAjaxPOSTRequests[request.url] = request;
			} else if (request.type === "DELETE") {
				mockAjaxDELETERequests[request.url] = request;
			}
		};
	};

var mockGoodCount = 0,
	mockBadCount = 0,
	mockGoodCountInc = function () {
		mockGoodCount++;
	},
	mockBadCountInc = function () {
		mockBadCount--;
	},
	mockGoodBadCounter = function () {
		mockGoodCount = 0;
		mockBadCount = 0;
	};

/**
 * maintenance-requests.js
 */
QUnit.test("maintenance-requests.setFormFieldLocation", function (assert) {
	// Create test objects
	var lat = 31.2,
		lng = 45.6;

	// Perform test
	setFormFieldLocation(lat, lng);
  	assert.ok('' + lat === document.getElementById("createMaintenanceRequestLatitude").value, "Passed!");
  	assert.ok('' + lng === document.getElementById("createMaintenanceRequestLongitude").value, "Passed!");
  	assert.ok('' + lat === document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML, "Passed!");
  	assert.ok('' + lng === document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML, "Passed!");
});

QUnit.test("maintenance-requests.setFormFieldLocation, rounded to two decimal places", function (assert) {
	// Create test objects
	var lat = 31.222,
		lng = 45.666,
		expectedLat = 31.22,
		expectedLng = 45.67;

	// Perform test
	setFormFieldLocation(lat, lng);
  	assert.ok('' + lat === document.getElementById("createMaintenanceRequestLatitude").value, "Passed!");
  	assert.ok('' + lng === document.getElementById("createMaintenanceRequestLongitude").value, "Passed!");
  	assert.ok('' + expectedLat === document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML, "Passed!");
  	assert.ok('' + expectedLng === document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML, "Passed!");
});

QUnit.test("maintenance-requests.setLocation", function (assert) {
	// Create test objects
	var position = {
		coords: {
			latitude: 31.2,
			longitude: 45.6
		}
	};
	mockMap();

	// Perform test
	setLocation(position);

	// Check location fields set
	assert.ok('' + position.coords.latitude === document.getElementById("createMaintenanceRequestLatitude").value, "Passed!");
  	assert.ok('' + position.coords.longitude === document.getElementById("createMaintenanceRequestLongitude").value, "Passed!");
  	assert.ok('' + position.coords.latitude === document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML, "Passed!");
  	assert.ok('' + position.coords.longitude === document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML, "Passed!");

  	// Check that location properly added
  	assert.ok(areMaintenanceRequestClicksPrioritized() === false, "Passed!");
  	assert.ok(assertDoubleCloseEnough(position.coords.latitude, getCurrentLocation().position.lat()), "Passed!");
  	assert.ok(assertDoubleCloseEnough(position.coords.longitude, getCurrentLocation().position.lng()), "Passed!");
  	assert.ok(map === getCurrentLocation().map, "Passed!");
  	assert.ok(16 === map.getZoom(), "Passed!");
  	assert.ok(mapPanToCounter === 1, "Passed!");
});

QUnit.test("maintenance-requests.getLocation, with location", function (assert) {
	// Create test objects
	var lat = 37.2,
		lng = 49.1;
	mockMap();
	mockGeolocation(true, lat, lng);

	// Perform test
	getLocation();

	// Check location fields set
	assert.ok('' + lat === document.getElementById("createMaintenanceRequestLatitude").value, "Passed!");
  	assert.ok('' + lng === document.getElementById("createMaintenanceRequestLongitude").value, "Passed!");
  	assert.ok('' + lat === document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML, "Passed!");
  	assert.ok('' + lng === document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML, "Passed!");

  	// Check that location properly added
  	assert.ok(areMaintenanceRequestClicksPrioritized() === false, "Passed!");
  	assert.ok(assertDoubleCloseEnough(lat, getCurrentLocation().position.lat()), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, getCurrentLocation().position.lng()), "Passed!");
  	assert.ok(map === getCurrentLocation().map, "Passed!");
  	assert.ok(16 === map.getZoom(), "Passed!");
  	assert.ok(mapPanToCounter === 1, "Passed!");
});

QUnit.test("maintenance-requests.getLocation, without location", function (assert) {
	// Create test objects
	mockGeolocation(false);
	mockWindowAlert();

	// Perform test
	getLocation();

	// Check that alert was fired
	assert.ok(alertCount === 1, "Passed!");
});

QUnit.test("maintenance-requests.allowMaintenanceRequestMapClick, undefined current location", function (assert) {
	// Create test objects
	mockMap();
	setCurrentLocation(undefined);
	mockWindowAlert();

	// Perform test
	allowMaintenanceRequestMapClick();

	assert.ok(getCurrentLocation() === undefined, "Passed!");
	assert.ok(alertCount === 1, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === true, "Passed!");
	assert.ok(mapListeners["click"].length === 1, "Passed!");
});

QUnit.test("maintenance-requests.allowMaintenanceRequestMapClick, null current location", function (assert) {
	// Create test objects
	mockMap();
	setCurrentLocation(null);
	mockWindowAlert();

	// Perform test
	allowMaintenanceRequestMapClick();

	assert.ok(getCurrentLocation() === null, "Passed!");
	assert.ok(alertCount === 1, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === true, "Passed!");
	assert.ok(mapListeners["click"].length === 1, "Passed!");
});

QUnit.test("maintenance-requests.allowMaintenanceRequestMapClick, actual current location", function (assert) {
	// Create test objects
	mockMap();
	setCurrentLocation(mockMapMarker(map));
	mockWindowAlert();

	// Perform test
	allowMaintenanceRequestMapClick();

	assert.ok(getCurrentLocation() === null, "Passed!");
	assert.ok(alertCount === 1, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === true, "Passed!");
	assert.ok(mapListeners["click"].length === 1, "Passed!");
});

QUnit.test("maintenance-requests.allowMaintenanceRequestMapClick, previous click listeners", function (assert) {
	// Create test objects
	mockMap();
	map.addListener("click", function (e) { console.log(e); });
	map.addListener("click", function (e) { console.log(e); });
	map.addListener("click", function (e) { console.log(e); });
	setCurrentLocation(undefined);
	mockWindowAlert();

	// Perform test
	allowMaintenanceRequestMapClick();

	assert.ok(getCurrentLocation() === undefined, "Passed!");
	assert.ok(alertCount === 1, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === true, "Passed!");
	assert.ok(mapListeners["click"].length === 1, "Passed!");
});

QUnit.test("maintenance-requests.maintenanceRequestClicked, previous click listeners and zoomed", function (assert) {
	// Create test objects
	mockMap();
	map.addListener("click", function (e) { console.log(e); });
	map.addListener("click", function (e) { console.log(e); });
	map.addListener("click", function (e) { console.log(e); });
	var lat = 31.2,
		lng = 45.1,
		fakeEvent = mockFakeLocationEvent(lat, lng);
	setZoomedIn(true);

	// Perform test
	maintenanceRequestClicked(fakeEvent);

	// Clear listeners, no longer prioritize maintenance requests
	assert.ok(mapListeners["click"] === undefined || mapListeners["click"].length === 0, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === false, "Passed!");

	// Set form field location
	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitude").value)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitude").value)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML)), "Passed!");

  	// Add current location to map
  	assert.ok(assertDoubleCloseEnough(lat, getCurrentLocation().position.lat()), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, getCurrentLocation().position.lng()), "Passed!");
  	assert.ok(map === getCurrentLocation().getMap(), "Passed!");
  	assert.ok(true === getCurrentLocation().getDraggable(), "Passed!");
  	// Can't test that 'dragend' event added
  	assert.ok(mapPanToCounter === 0, "Passed!"); // Not panned when zoomed
  	assert.ok(16 === map.getZoom(), "Passed!");
  	assert.ok(true === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.maintenanceRequestClicked, not zoomed in", function (assert) {
	// Create test objects
	mockMap();
	var lat = 29.0,
		lng = 1.1,
		fakeEvent = mockFakeLocationEvent(lat, lng);
	setZoomedIn(false);

	// Perform test
	maintenanceRequestClicked(fakeEvent);

	// Clear listeners, no longer prioritize maintenance requests
	assert.ok(mapListeners["click"] === undefined || mapListeners["click"].length === 0, "Passed!");
	assert.ok(areMaintenanceRequestClicksPrioritized() === false, "Passed!");

	// Set form field location
	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitude").value)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitude").value)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML)), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML)), "Passed!");

  	// Add current location to map
  	assert.ok(assertDoubleCloseEnough(lat, getCurrentLocation().position.lat()), "Passed!");
  	assert.ok(assertDoubleCloseEnough(lng, getCurrentLocation().position.lng()), "Passed!");
  	assert.ok(map === getCurrentLocation().getMap(), "Passed!");
  	assert.ok(true === getCurrentLocation().getDraggable(), "Passed!");
  	// Can't test that 'dragend' event added
  	assert.ok(mapPanToCounter === 1, "Passed!"); // Panned when not zoomed
  	assert.ok(16 === map.getZoom(), "Passed!");
  	assert.ok(true === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.doneDraggingMarker, fake location", function (assert) {
	// Create test objects
	var lat = 9.8,
		lng = -12.2,
		fakeEvent = mockFakeLocationEvent(lat, lng);

	// Perform test
	doneDraggingMarker(fakeEvent);

	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitude").value)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitude").value)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML)), "Passed!");
});

QUnit.test("maintenance-requests.doneDraggingMarker, with another fake location", function (assert) {
	// Create test objects
	var lat = -89.1,
		lng = 3.4,
		fakeEvent = mockFakeLocationEvent(lat, lng);

	// Perform test
	doneDraggingMarker(fakeEvent);

	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitude").value)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitude").value)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, parseFloat(document.getElementById("createMaintenanceRequestLatitudeDisplay").innerHTML)), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat(document.getElementById("createMaintenanceRequestLongitudeDisplay").innerHTML)), "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, actual location provided", function (assert) {
	// Create test objects
	var lat = -31.03,
		lng = 29.1234,
		locationString = "-31.03,29.1234";

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(assertDoubleCloseEnough(lat, result.lat), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, result.lng), "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, undefined location provided", function (assert) {
	// Create test objects
	var locationString = undefined;

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(result === null, "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, null location provided", function (assert) {
	// Create test objects
	var locationString = null;

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(result === null, "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, no location provided", function (assert) {
	// Create test objects
	var locationString = "abaksdkas ajlkajskdjaks kjakl";

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(result === null, "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, too few numbers provided", function (assert) {
	// Create test objects
	var lat = -31.03,
		locationString = "-31.03";

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(result === null, "Passed!");
});

QUnit.test("maintenance-requests.parseLatLng, too many numbers provided", function (assert) {
	// Create test objects
	var lat = -31.03,
		lng = 29.1234,
		locationString = "-31.03, 29.1234, 17.0123";

	// Perform test
	var result = parseLatLng(locationString);
	assert.ok(result === null, "Passed!");
});

QUnit.test("maintenance-requests.clearRequestsOnMap, undefined requests", function (assert) {
	// Create test objects
	setMaintenanceRequestsOnMap(undefined);

	// Perform test
	clearRequestsOnMap();

	assert.ok(undefined === getMaintenanceRequestsOnMap(), "Passed!");
});

QUnit.test("maintenance-requests.clearRequestsOnMap, null requests", function (assert) {
	// Create test objects
	setMaintenanceRequestsOnMap(null);

	// Perform test
	clearRequestsOnMap();

	assert.ok(null === getMaintenanceRequestsOnMap(), "Passed!");
});

QUnit.test("maintenance-requests.clearRequestsOnMap, no requests", function (assert) {
	// Create test objects
	setMaintenanceRequestsOnMap([]);

	// Perform test
	clearRequestsOnMap();

	assert.ok(0 === getMaintenanceRequestsOnMap().length, "Passed!");
});

QUnit.test("maintenance-requests.clearRequestsOnMap, several requests", function (assert) {
	// Create test objects
	mockMap();
	var that = this,
		fakeRequests = [1, 2, 3].map(function (pk) { return mockMaintenanceRequest(map, pk); });
	setMaintenanceRequestsOnMap(fakeRequests);

	// Perform test
	clearRequestsOnMap();

	assert.ok(0 === getMaintenanceRequestsOnMap().length, "Passed!");
});

QUnit.test("maintenance-requests.addRequestToMap, not resolved", function (assert) {
	// Create test objects
	mockMap();
	setMaintenanceRequestsOnMap([]);
	var pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp);

	// Perform test
	addRequestToMap(fakeRequest);

	assert.ok(1 === getMaintenanceRequestsOnMap().length, "Passed!");

	var mr = getMaintenanceRequestsOnMap()[0];
	assert.ok(pk === mr.id, "Passed!");
	assert.ok(undefined !== mr.marker, "Passed!");
	assert.ok("#" + pk === mr.marker.getTitle(), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, mr.marker.getPosition().lat()), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, mr.marker.getPosition().lng()), "Passed!");
	assert.ok(typeof(mr.marker.getIcon()) === "string", "Passed!");
	assert.ok(mr.marker.getIcon().indexOf("red-dot") > -1, "Passed!");
	assert.ok(map === mr.marker.getMap(), "Passed!");
	assert.ok(mapPanToCounter === 0, "Passed!");

	// Check for tooltip
	assert.ok(undefined !== mr.infoWindow, "Passed!");
	assert.ok(mr.infoWindow.getContent().length > 0, "Passed!");

	// Test clicking marker
	google.maps.event.trigger(mr.marker, "click", {latLng: new google.maps.LatLng(lat, lng)});
	assert.ok(mapPanToCounter === 1, "Passed!");
	assert.ok(16 === map.getZoom(), "Passed!");
	assert.ok(true === isZoomedIn(), "Passed!");
	// Tooltip popped up
	assert.ok(assertDoubleCloseEnough(lat + 0.0005, mr.infoWindow.getPosition().lat()), "Passed!"); // Slightly above
	assert.ok(assertDoubleCloseEnough(lng, mr.infoWindow.getPosition().lng()), "Passed!");
});

QUnit.test("maintenance-requests.addRequestToMap, resolved", function (assert) {
	// Create test objects
	mockMap();
	setMaintenanceRequestsOnMap([]);
	var pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = true,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:46:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp);

	// Perform test
	addRequestToMap(fakeRequest);

	assert.ok(1 === getMaintenanceRequestsOnMap().length, "Passed!");

	var mr = getMaintenanceRequestsOnMap()[0];
	assert.ok(pk === mr.id, "Passed!");
	assert.ok(undefined !== mr.marker, "Passed!");
	assert.ok("#" + pk === mr.marker.getTitle(), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, mr.marker.getPosition().lat()), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, mr.marker.getPosition().lng()), "Passed!");
	assert.ok(typeof(mr.marker.getIcon()) === "string", "Passed!");
	assert.ok(mr.marker.getIcon().indexOf("green-dot") > -1, "Passed!");
	assert.ok(map === mr.marker.getMap(), "Passed!");
	assert.ok(mapPanToCounter === 0, "Passed!");

	// Check for tooltip
	assert.ok(undefined !== mr.infoWindow, "Passed!");
	assert.ok(mr.infoWindow.getContent().length > 0, "Passed!");

	// Test clicking marker
	google.maps.event.trigger(mr.marker, "click", {latLng: new google.maps.LatLng(lat, lng)});
	assert.ok(mapPanToCounter === 1, "Passed!");
	assert.ok(16 === map.getZoom(), "Passed!");
	assert.ok(true === isZoomedIn(), "Passed!");
	// Tooltip popped up
	assert.ok(assertDoubleCloseEnough(lat + 0.0005, mr.infoWindow.getPosition().lat()), "Passed!"); // Slightly above
	assert.ok(assertDoubleCloseEnough(lng, mr.infoWindow.getPosition().lng()), "Passed!");
});

QUnit.test("maintenance-requests.attachMaintenanceRequestTooltip", function (assert) {
	// Create test objects
	mockMap();
	var lat = 31.4,
		lng = -122.2,
		fakeRequest = mockMaintenanceRequest(map, 1, lat, lng),
		content = "This is my content";

	// Perform test
	attachMaintenanceRequestTooltip(fakeRequest, content, map);

	assert.ok(undefined !== fakeRequest.infoWindow, "Passed!");
	assert.ok(content === fakeRequest.infoWindow.getContent(), "Passed!");

	// Test clicking marker
	google.maps.event.trigger(fakeRequest.marker, "click", {latLng: new google.maps.LatLng(lat, lng)});
	assert.ok(assertDoubleCloseEnough(lat + 0.0005, fakeRequest.infoWindow.getPosition().lat()), "Passed!"); // Slightly above
	assert.ok(assertDoubleCloseEnough(lng, fakeRequest.infoWindow.getPosition().lng()), "Passed!");
});

QUnit.test("maintenance-requests.attachMaintenanceRequestTooltip, test opening on click", function (assert) {
	// Create test objects
	mockMap();
	var lat = 31.4,
		lng = -122.2,
		fakeRequest = mockMaintenanceRequest(map, 1, lat, lng),
		content = "This is my content";

	// Perform test
	attachMaintenanceRequestTooltip(fakeRequest, content, map);

	// Override open on actual info window
	fakeRequest.infoWindow.open = mockInfoWindowOpen;
	resetMockInfoWindowCounts(); 

	// Test clicking marker
	google.maps.event.trigger(fakeRequest.marker, "click", {latLng: new google.maps.LatLng(lat, lng)});
	assert.ok(assertDoubleCloseEnough(lat + 0.0005, fakeRequest.infoWindow.getPosition().lat()), "Passed!"); // Slightly above
	assert.ok(assertDoubleCloseEnough(lng, fakeRequest.infoWindow.getPosition().lng()), "Passed!");
	assert.ok(1 === infoWindowOpenCount, "Passed!");
});

QUnit.test("maintenance-requests.hideMaintenanceRequestInfoWindows, no requests", function (assert) {
	// Create test objects
	setMaintenanceRequestsOnMap([]);
	resetMockInfoWindowCounts();

	// Perform test
	hideMaintenanceRequestInfoWindows();

	assert.ok(0 === infoWindowCloseCount, "Passed!");
});

QUnit.test("maintenance-requests.hideMaintenanceRequestInfoWindows, several requests", function (assert) {
	// Create test objects
	setMaintenanceRequestsOnMap([{infoWindow: mockInfoWindow("A")}, {infoWindow: mockInfoWindow("B")}, {infoWindow: mockInfoWindow("C")}]);
	resetMockInfoWindowCounts();

	// Perform test
	hideMaintenanceRequestInfoWindows();

	assert.ok(3 === infoWindowCloseCount, "Passed!");
});

QUnit.test("maintenance-requests.zoomToRequest, undefined requests", function (assert) {
	// Create test objects
	var requestNum = 1;
	mockMap();
	setMaintenanceRequestsOnMap(undefined);
	setZoomedIn(false);


	// Perform test
	zoomToRequest(requestNum);

	assert.ok(0 === mapPanToCounter, "Passed!");
	assert.ok(false === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.zoomToRequest, null requests", function (assert) {
	// Create test objects
	var requestNum = 1;
	mockMap();
	setMaintenanceRequestsOnMap(null);
	setZoomedIn(false);


	// Perform test
	zoomToRequest(requestNum);

	assert.ok(0 === mapPanToCounter, "Passed!");
	assert.ok(false === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.zoomToRequest, no requests", function (assert) {
	// Create test objects
	var requestNum = 1;
	mockMap();
	setMaintenanceRequestsOnMap([]);
	setZoomedIn(false);


	// Perform test
	zoomToRequest(requestNum);

	assert.ok(0 === mapPanToCounter, "Passed!");
	assert.ok(false === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.zoomToRequest, invalid request number", function (assert) {
	// Create test objects
	var requestNum = 1;
	mockMap();
	setMaintenanceRequestsOnMap([0, 2, 3].map(function (pk) { return mockMaintenanceRequest(map, pk); }));
	setZoomedIn(false);


	// Perform test
	zoomToRequest(requestNum);

	assert.ok(0 === mapPanToCounter, "Passed!");
	assert.ok(false === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.zoomToRequest, valid request number", function (assert) {
	// Create test objects
	var requestNum = 1;
	mockMap();
	setMaintenanceRequestsOnMap([1, 2, 3].map(function (pk) { return mockMaintenanceRequest(map, pk); }));
	setZoomedIn(false);


	// Perform test
	zoomToRequest(requestNum);

	assert.ok(1 === mapPanToCounter, "Passed!");
	assert.ok(true === isZoomedIn(), "Passed!");
});

QUnit.test("maintenance-requests.getRequests, show requests and successful with no requests", function (assert) {
	// Create test objects
	var showRequests = true,
		urlCalled = "../rtfapp/maintenance-requests/",
		maintenanceRequestsReturned = [];
	mockAjaxCall();
	mockHideOtherViews();

	// Perform test
	getRequests(showRequests);
	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	ajaxRequest.success(maintenanceRequestsReturned);

	assert.ok(0 === getMaintenanceRequestsOnMap().length, "Passed!");
	assert.ok(1 === hideOtherViewsCount, "Passed!");
});

QUnit.test("maintenance-requests.getRequests, show requests and successful with a couple of requests", function (assert) {
	// Create test objects
	var showRequests = true,
		urlCalled = "../rtfapp/maintenance-requests/",
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp),
		maintenanceRequestsReturned = [fakeRequest, fakeRequest];

	mockAjaxCall();
	mockHideOtherViews();

	// Perform test
	getRequests(showRequests);
	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	ajaxRequest.success(maintenanceRequestsReturned);

	assert.ok(2 === getMaintenanceRequestsOnMap().length, "Passed!");
	assert.ok(1 === hideOtherViewsCount, "Passed!");
});

QUnit.test("maintenance-requests.getRequests and maintenanceRequestDivClicked, test clicking a maintenance request", function (assert) {
	// Create test objects
	var showRequests = true,
		urlCalled = "../rtfapp/maintenance-requests/",
		pk1 = 1,
		pk2 = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest1 = mockMaintenanceRequestFromServer(pk1, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp);
		fakeRequest2 = mockMaintenanceRequestFromServer(pk2, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp),
		divID1 = "#mRequest" + pk1,
		divID2 = "#mRequest" + pk2,
		maintenanceRequestsReturned = [fakeRequest1, fakeRequest2];

	mockAjaxCall();
	mockHideOtherViews();

	// Perform test
	getRequests(showRequests);
	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	ajaxRequest.success(maintenanceRequestsReturned);

	assert.ok(2 === getMaintenanceRequestsOnMap().length, "Passed!");
	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok(-1 === getOpenRequest(), "Passed!");

	// First click on pk 1
	$(divID1).click();
	assert.ok(1 === getOpenRequest(), "Passed!");
	assert.ok(true === $(divID1).hasClass("selected"), "Passed!");

	// Second click on pk 2
	$(divID2).click();
	assert.ok(2 === getOpenRequest(), "Passed!");
	assert.ok(false === $(divID1).hasClass("selected"), "Passed!");
	assert.ok(true === $(divID2).hasClass("selected"), "Passed!");

	// Third click on pk 2
	$(divID2).click();
	assert.ok(-1 === getOpenRequest(), "Passed!");
	assert.ok(false === $(divID2).hasClass("selected"), "Passed!");
});

QUnit.test("maintenance-requests.getRequests, error", function (assert) {
	// Create test objects
	var showRequests = true,
		urlCalled = "../rtfapp/maintenance-requests/";
	mockAjaxCall();
	mockHideOtherViews();

	// Perform test
	getRequests(showRequests);
	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	ajaxRequest.error(null, "error", null);

	assert.ok(0 === hideOtherViewsCount, "Passed!");
});

QUnit.test("maintenance-requests.editSpecificRequest", function (assert) {
	// Create test objects
	var requestNum = 2,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	mockHideOtherViews();
	setMaintenanceRequests(fakeMaintenanceRequests);

	// Perform test
	editSpecificRequest(requestNum);

	// assume hide info windows can function properly on its own
	// show request
	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok(description === $("textarea[name=editMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok(createdBy === $("input[name=editMaintenanceRequestUser]").val(), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, parseFloat($("span#editMaintenanceRequestLatitude").html())), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat($("span#editMaintenanceRequestLongitude").html())), "Passed!");
	assert.ok("false" === $("select[name=editMaintenanceRequestResolved]").val(), "Passed!");
});

QUnit.test("maintenance-requests.showEditRequest, with request number and not resolved", function (assert) {
	// Create test objects
	var showRequest = true,
		requestNum = 2,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	mockHideOtherViews();
	setMaintenanceRequests(fakeMaintenanceRequests);
	setOpenRequest(requestNum);

	// Perform test
	showEditRequest(showRequest);

	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok(description === $("textarea[name=editMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok(createdBy === $("input[name=editMaintenanceRequestUser]").val(), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, parseFloat($("span#editMaintenanceRequestLatitude").html())), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat($("span#editMaintenanceRequestLongitude").html())), "Passed!");
	assert.ok("false" === $("select[name=editMaintenanceRequestResolved]").val(), "Passed!");
});

QUnit.test("maintenance-requests.showEditRequest, with request number and resolved", function (assert) {
	// Create test objects
	var showRequest = true,
		requestNum = 2,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = true,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	mockHideOtherViews();
	setMaintenanceRequests(fakeMaintenanceRequests);
	setOpenRequest(requestNum);

	// Perform test
	showEditRequest(showRequest);

	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok(description === $("textarea[name=editMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok(createdBy === $("input[name=editMaintenanceRequestUser]").val(), "Passed!");
	assert.ok(assertDoubleCloseEnough(lat, parseFloat($("span#editMaintenanceRequestLatitude").html())), "Passed!");
	assert.ok(assertDoubleCloseEnough(lng, parseFloat($("span#editMaintenanceRequestLongitude").html())), "Passed!");
	assert.ok("true" === $("select[name=editMaintenanceRequestResolved]").val(), "Passed!");
});

QUnit.test("maintenance-requests.showEditRequest, with request number and hide", function (assert) {
	// Create test objects
	var showRequest = false,
		requestNum = 2,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	mockHideOtherViews();
	setMaintenanceRequests(fakeMaintenanceRequests);
	setOpenRequest(requestNum);

	// Perform test
	showEditRequest(showRequest);

	assert.ok(1 === hideOtherViewsCount, "Passed!");
});

QUnit.test("maintenance-requests.showEditRequest, with invalid request number", function (assert) {
	// Create test objects
	var showRequest = false,
		requestNum = 1,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	mockHideOtherViews();
	setMaintenanceRequests(fakeMaintenanceRequests);
	setOpenRequest(requestNum);

	// Perform test
	showEditRequest(showRequest);

	assert.ok(1 === hideOtherViewsCount, "Passed!");
});

QUnit.test("maintenance-requests.editRequest, some invalid fields", function (assert) {
	// Create test objects
	var requestNum = 1,
		description = "",
		user = "Michael",
		resolved = "false",
		lat = -31.2,
		lng = 54.2,
		urlCalled = "../rtfapp/maintenance-requests/" + requestNum + "/";

	setOpenRequest(requestNum);
	$("textarea[name=editMaintenanceRequestDescription]").val(description);
	$("input[name=editMaintenanceRequestUser]").val(user);
	$("select[name=editMaintenanceRequestResolved]").val(resolved);
	$("span#editMaintenanceRequestLatitude").html("" + lat);
	$("span#editMaintenanceRequestLongitude").html("" + lng);

	mockAjaxCall();

	// Perform test
	editRequest();

	// Background color for valid/invalid
	assert.ok("#FF5151" === rgbStrToHex(getCSSByName("editMaintenanceRequestDescription", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("editMaintenanceRequestUser", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("editMaintenanceRequestResolved", "background-color")), "Passed!");

	// No post request
	assert.ok(undefined === mockAjaxPOSTRequests[urlCalled], "Passed!");
});

QUnit.test("maintenance-requests.editRequest, valid fields", function (assert) {
	// Create test objects
	var requestNum = 1,
		description = "This is a description.",
		user = "Michael",
		resolved = "false",
		lat = -31.2,
		lng = 54.2,
		urlCalled = "../rtfapp/maintenance-requests/" + requestNum + "/",
		getReqeustsUrl = "../rtfapp/maintenance-requests/";

	setOpenRequest(requestNum);
	$("textarea[name=editMaintenanceRequestDescription]").val(description);
	$("input[name=editMaintenanceRequestUser]").val(user);
	$("select[name=editMaintenanceRequestResolved]").val(resolved);
	$("span#editMaintenanceRequestLatitude").html("" + lat);
	$("span#editMaintenanceRequestLongitude").html("" + lng);

	mockAjaxCall();

	// Perform test
	editRequest();

	// Background color for valid/invalid
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("editMaintenanceRequestDescription", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("editMaintenanceRequestUser", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("editMaintenanceRequestResolved", "background-color")), "Passed!");

	// Post request
	var request = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== request, "Passed!");
	assert.ok(undefined === mockAjaxGETRequests[getReqeustsUrl], "Passed!");

	// Call success
	request.success();
	assert.ok(undefined !== mockAjaxGETRequests[getReqeustsUrl], "Passed!");

	// Call error
	request.error(null, "error", null);
});

QUnit.test("maintenance-requests.showCreateRequest, open", function (assert) {
	// Create test objects
	var open = true,
		description = "",
		user = "Michael",
		lat = -31.2,
		lng = 51.4;

	$("textarea[name=createMaintenanceRequestDescription]").val(description);
	$("input[name=createMaintenanceRequestUser]").val(user);
	$("input[name=createMaintenanceRequestLatitude]").val("" + lat);
	$("input[name=createMaintenanceRequestLongitude]").val("" + lng);
	$("span#createMaintenanceRequestLatitude").html("" + lat);
	$("span#createMaintenanceRequestLongitude").html("" + lng);

	mockHideOtherViews();

	// Perform test
	showCreateRequest(open);

	// Cleared fields
	assert.ok("" === $("textarea[name=createMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestUser]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLatitude]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLongitude]").val(), "Passed!");
	assert.ok("NaN" === $("span#createMaintenanceRequestLatitude").html(), "Passed!");
	assert.ok("NaN" === $("span#createMaintenanceRequestLongitude").html(), "Passed!");

	// Valid show/hides
	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok("none" === $("#maintenanceRequests").css("display"), "Passed!");
	assert.ok("none" === $("#editMaintenanceRequest").css("display"), "Passed!");
	assert.ok("none" !== $("#createMaintenanceRequest").css("display"), "Passed!");

	// Removed current map location
	assert.ok(undefined === getCurrentLocation() || null === getCurrentLocation(), "Passed!");
	assert.ok(false === areMaintenanceRequestClicksPrioritized(), "Passed!");
});

QUnit.test("maintenance-requests.showCreateRequest, closed", function (assert) {
	// Create test objects
	var open = false,
		description = "",
		user = "Michael",
		lat = -31.2,
		lng = 51.4;

	$("textarea[name=createMaintenanceRequestDescription]").val(description);
	$("input[name=createMaintenanceRequestUser]").val(user);
	$("input[name=createMaintenanceRequestLatitude]").val("" + lat);
	$("input[name=createMaintenanceRequestLongitude]").val("" + lng);
	$("span#createMaintenanceRequestLatitude").html("" + lat);
	$("span#createMaintenanceRequestLongitude").html("" + lng);

	mockHideOtherViews();

	// Perform test
	showCreateRequest(open);

	// Cleared fields
	assert.ok("" === $("textarea[name=createMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestUser]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLatitude]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLongitude]").val(), "Passed!");
	assert.ok("NaN" === $("span#createMaintenanceRequestLatitude").html(), "Passed!");
	assert.ok("NaN" === $("span#createMaintenanceRequestLongitude").html(), "Passed!");

	// Valid show/hides
	assert.ok(1 === hideOtherViewsCount, "Passed!");
	assert.ok("none" !== $("#maintenanceRequests").css("display"), "Passed!");
	assert.ok("none" === $("#editMaintenanceRequest").css("display"), "Passed!");
	assert.ok("none" === $("#createMaintenanceRequest").css("display"), "Passed!");

	// Removed current map location
	assert.ok(undefined === getCurrentLocation() || null === getCurrentLocation(), "Passed!");
	assert.ok(false === areMaintenanceRequestClicksPrioritized(), "Passed!");
});

QUnit.test("maintenance-requests.createRequest, invalid fields", function (assert) {
	// Create test objects
	var description = "",
		user = "Michael",
		lat = "",
		lng = 51.4,
		urlCalled = "../rtfapp/maintenance-requests/";

	$("textarea[name=createMaintenanceRequestDescription]").val(description);
	$("input[name=createMaintenanceRequestUser]").val(user);
	$("input[name=createMaintenanceRequestLatitude]").val("" + lat);
	$("input[name=createMaintenanceRequestLongitude]").val("" + lng);
	$("span#createMaintenanceRequestLatitude").html("" + lat);
	$("span#createMaintenanceRequestLongitude").html("" + lng);

	mockAjaxCall();

	// Perform test
	createRequest();

	// Background color for valid/invalid
	assert.ok("#FF5151" === rgbStrToHex(getCSSByName("createMaintenanceRequestDescription", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestUser", "background-color")), "Passed!");
	assert.ok("#FF5151" === rgbStrToHex(getCSSByName("createMaintenanceRequestLatitude", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestLongitude", "background-color")), "Passed!");

	// Post request not made
	assert.ok(undefined === mockAjaxGETRequests[urlCalled], "Passed!");
});


QUnit.test("maintenance-requests.createRequest, valid fields", function (assert) {
	// Create test objects
	var description = "This is a description.",
		user = "Michael",
		lat = -31.2,
		lng = 51.4,
		urlCalled = "../rtfapp/maintenance-requests/",
		urlGetRequests = "../rtfapp/maintenance-requests/"
		successfulData = {success: true};

	$("textarea[name=createMaintenanceRequestDescription]").val(description);
	$("input[name=createMaintenanceRequestUser]").val(user);
	$("input[name=createMaintenanceRequestLatitude]").val("" + lat);
	$("input[name=createMaintenanceRequestLongitude]").val("" + lng);
	$("span#createMaintenanceRequestLatitude").html("" + lat);
	$("span#createMaintenanceRequestLongitude").html("" + lng);

	mockAjaxCall();
	mockTimeouts();

	// Perform test
	createRequest();

	// Background color for valid/invalid
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestDescription", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestUser", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestLatitude", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestLongitude", "background-color")), "Passed!");

	// Post request made
	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Success for request
	ajaxRequest.success(successfulData);
	// Displayed right after
	assert.ok("block" === $("#mrequestMessage").css("display"), "Passed!");
	// Timeout set
	assert.ok(1 === timeouts.length, "Passed!");
	assert.ok(5000 === timeouts[0].time, "Passed!");
	timeouts[0].fcn(); // Call timeout function
	assert.ok("none" === $("#mrequestMessage").css("display"), "Passed!");
	// Cleared background colors
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestDescription", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestUser", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestLatitude", "background-color")), "Passed!");
	assert.ok("#FFFFFF" === rgbStrToHex(getCSSByName("createMaintenanceRequestLongitude", "background-color")), "Passed!");
	// Cleared fields
	assert.ok("" === $("textarea[name=createMaintenanceRequestDescription]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestUser]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLatitude]").val(), "Passed!");
	assert.ok("" === $("input[name=createMaintenanceRequestLongitude]").val(), "Passed!");
	// Removed current map location
	assert.ok(undefined === getCurrentLocation() || null === getCurrentLocation(), "Passed!");
	assert.ok(false === areMaintenanceRequestClicksPrioritized(), "Passed!");
	// Get requests
	assert.ok(undefined !== mockAjaxGETRequests[urlGetRequests], "Passed!");

	// Error for request
	ajaxRequest.error(null, "error", null);
});

QUnit.test("maintenance-requests.resolveSpecificRequest", function (assert) {
	// Create test objects
	var requestNum = 2,
		urlCalled = "../rtfapp/maintenance-requests/" + requestNum + "/",
		urlGetRequests = "../rtfapp/maintenance-requests/";

	mockAjaxCall();

	// Perform test
	resolveSpecificRequest(requestNum);

	assert.ok(requestNum === getOpenRequest(), "Passed!");
	// Assume hides info windows
	// Resolves request
	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
	assert.ok(true === ajaxRequest.data.resolved, "Passed!");
	// Success function
	ajaxRequest.success();
	assert.ok(undefined !== mockAjaxGETRequests[urlGetRequests], "Passed!");
	// Error function
	ajaxRequest.error(null, "error", null);
});

QUnit.test("maintenance-requests.resolveRequest", function (assert) {
	// Create test objects
	var requestNum = 1,
		urlCalled = "../rtfapp/maintenance-requests/" + requestNum + "/",
		urlGetRequests = "../rtfapp/maintenance-requests/";
	setOpenRequest(requestNum);

	mockAjaxCall();

	// Perform test
	resolveRequest();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
	assert.ok(true === ajaxRequest.data.resolved, "Passed!");

	// Success function
	assert.ok(undefined === mockAjaxGETRequests[urlGetRequests], "Passed!");
	ajaxRequest.success();
	assert.ok(undefined !== mockAjaxGETRequests[urlGetRequests], "Passed!");

	// Error function
	ajaxRequest.error(null, "error", null);
});

QUnit.test("maintenance-requests.deleteRequest", function (assert) {
	// Create test objects
	var requestNum = 3,
		urlCalled = "../rtfapp/maintenance-requests/" + requestNum + "/",
		urlGetRequests = "../rtfapp/maintenance-requests/";

	setOpenRequest(requestNum);

	mockAjaxCall();

	// Perform test
	deleteRequest();

	var ajaxRequest = mockAjaxDELETERequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
	// Success function
	assert.ok(undefined === mockAjaxGETRequests[urlGetRequests], "Passed!");
	ajaxRequest.success();
	assert.ok(undefined !== mockAjaxGETRequests[urlGetRequests], "Passed!");
	// Error function
	ajaxRequest.error(null, "error", null);
});

QUnit.test("maintenance-requests.getRequestWithId, invalid id", function (assert) {
	// Create test objects
	var requestNum = 1,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	// Perform test
	var result = getRequestWithId(requestNum);
	assert.ok(-1 === result, "Passed!");
});

QUnit.test("maintenance-requests.getRequestWithId, valid id", function (assert) {
	// Create test objects
	var requestNum = 2,
		pk = 2,
		lat = -31.2,
		lng = 54.2,
		resolved = false,
		description = "This is my description.",
		createdBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, resolved, description, createdBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	// Perform test
	var result = getRequestWithId(requestNum);
	assert.ok(fakeRequest === result, "Passed!");
});

QUnit.test("maintenance-requests.onFilterChange, new values but no matches", function (assert) {
	// Create test objects
	var description = "This is a description.",
		descriptionFilter = "description",
		descriptionFilterId = "#descriptionFilter",
		createdBy = "Michael",
		createdByFilter = "created_by",
		createdByFilterId = "#created_byFilter",
		resolved = "false",
		resolvedFilter = "resolved",
		resolvedFilterId = "#resolvedFilter",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = true,
		mrDescription = "This is not my description.",
		mrCreatedBy = "Kyle",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	$(descriptionFilterId).val(description);
	$(createdByFilterId).val(createdBy);
	$(resolvedFilterId).val(resolved);

	// Perform test
	onFilterChange(descriptionFilter);
	onFilterChange(createdByFilter);
	onFilterChange(resolvedFilter);
	assert.ok(description === getFilterValue(descriptionFilter), "Passed!");
	assert.ok(createdBy === getFilterValue(createdByFilter), "Passed!");
	assert.ok(resolved === getFilterValue(resolvedFilter), "Passed!");
	assert.ok("block" === $("#noRequests").css("display"), "Passed!");
	assert.ok("none" === $("#mRequest" + pk).css("display"), "Passed!");

	// Cleanup
	resetFilters();
});

QUnit.test("maintenance-requests.applyFilters, new description and resolved match", function (assert) {
	// Create test objects
	var description = "This is a description.",
		descriptionFilter = "description",
		descriptionFilterId = "#descriptionFilter",
		createdBy = "Michael",
		createdByFilter = "created_by",
		createdByFilterId = "#created_byFilter",
		resolved = "true",
		resolvedFilter = "resolved",
		resolvedFilterId = "#resolvedFilter",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = true,
		mrDescription = "This is a description.",
		mrCreatedBy = "Kyle",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	$(descriptionFilterId).val(description);
	$(resolvedFilterId).val(resolved);
	onFilterChange(descriptionFilter);
	onFilterChange(resolvedFilter);

	// Perform test
	applyFilters();
	assert.ok(description === getFilterValue(descriptionFilter), "Passed!");
	assert.ok(resolved === getFilterValue(resolvedFilter), "Passed!");
	assert.ok("none" === $("#noRequests").css("display"), "Passed!");
	assert.ok("block" === $("#mRequest" + pk).css("display"), "Passed!");

	// Cleanup
	resetFilters();
});

QUnit.test("maintenance-requests.applyFilters, new description and resolved but no createdBy match", function (assert) {
	// Create test objects
	var description = "This is a description.",
		descriptionFilter = "description",
		descriptionFilterId = "#descriptionFilter",
		createdBy = "Michael",
		createdByFilter = "created_by",
		createdByFilterId = "#created_byFilter",
		resolved = "true",
		resolvedFilter = "resolved",
		resolvedFilterId = "#resolvedFilter",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = true,
		mrDescription = "This is a description.",
		mrCreatedBy = "Kyle",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	$(descriptionFilterId).val(description);
	$(resolvedFilterId).val(resolved);
	$(createdByFilterId).val(createdBy);
	onFilterChange(descriptionFilter);
	onFilterChange(resolvedFilter);
	onFilterChange(createdByFilter);

	// Perform test
	applyFilters();
	assert.ok(description === getFilterValue(descriptionFilter), "Passed!");
	assert.ok(resolved === getFilterValue(resolvedFilter), "Passed!");
	assert.ok(createdBy === getFilterValue(createdByFilter), "Passed!");
	assert.ok("block" === $("#noRequests").css("display"), "Passed!");
	assert.ok("none" === $("#mRequest" + pk).css("display"), "Passed!");

	// Cleanup
	resetFilters();
});

QUnit.test("maintenance-requests.applyFilters, remove selected match when filtered out", function (assert) {
	// Create test objects
	var description = "This is a description.",
		descriptionFilter = "description",
		descriptionFilterId = "#descriptionFilter",
		createdBy = "Michael",
		createdByFilter = "created_by",
		createdByFilterId = "#created_byFilter",
		resolved = "true",
		resolvedFilter = "resolved",
		resolvedFilterId = "#resolvedFilter",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = true,
		mrDescription = "This is not a description.",
		mrCreatedBy = "Michael",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	setOpenRequest(pk);
	$("#mRequest" + pk).addClass("selected");

	$(descriptionFilterId).val(description);
	$(resolvedFilterId).val(resolved);
	$(createdByFilterId).val(createdBy);
	onFilterChange(descriptionFilter);
	onFilterChange(resolvedFilter);
	onFilterChange(createdByFilter);

	// Perform test
	applyFilters();
	assert.ok(description === getFilterValue(descriptionFilter), "Passed!");
	assert.ok(resolved === getFilterValue(resolvedFilter), "Passed!");
	assert.ok(createdBy === getFilterValue(createdByFilter), "Passed!");
	assert.ok("block" === $("#noRequests").css("display"), "Passed!");
	assert.ok("none" === $("#mRequest" + pk).css("display"), "Passed!");
	assert.ok(false === $("mRequest" + pk).hasClass("selected"), "Passed!");
	assert.ok(-1 === getOpenRequest(), "Passed!");

	// Cleanup
	resetFilters();
});

QUnit.test("maintenance-requests.clearFilters, not resolved match", function (assert) {
	// Create test objects
	var descriptionFilter = "description",
		createdByFilter = "created_by",
		resolvedFilter = "resolved",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = false,
		mrDescription = "This is a description.",
		mrCreatedBy = "Kyle",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	// Perform test
	clearFilters();
	assert.ok("" === getFilterValue(descriptionFilter), "Passed!");
	assert.ok("false"=== getFilterValue(resolvedFilter), "Passed!");
	assert.ok("" === getFilterValue(createdByFilter), "Passed!");
	assert.ok("none" === $("#noRequests").css("display"), "Passed!");
	assert.ok("block" === $("#mRequest" + pk).css("display"), "Passed!");
});

QUnit.test("maintenance-requests.clearFilters, no default matches", function (assert) {
	// Create test objects
	var descriptionFilter = "description",
		createdByFilter = "created_by",
		resolvedFilter = "resolved",
		pk = 1,
		lat = -31.2,
		lng = 54.2,
		mrResolved = true,
		mrDescription = "This is a description.",
		mrCreatedBy = "Kyle",
		submitTimestamp = "March 6, 2016 09:12:00",
		fakeRequest = mockMaintenanceRequestFromServer(pk, "" + lat + "," + lng, mrResolved, mrDescription, mrCreatedBy, submitTimestamp)
		fakeMaintenanceRequests = [fakeRequest];

	setMaintenanceRequests(fakeMaintenanceRequests);

	// Perform test
	clearFilters();
	assert.ok("" === getFilterValue(descriptionFilter), "Passed!");
	assert.ok("false"=== getFilterValue(resolvedFilter), "Passed!");
	assert.ok("" === getFilterValue(createdByFilter), "Passed!");
	assert.ok("block" === $("#noRequests").css("display"), "Passed!");
	assert.ok("none" === $("#mRequest" + pk).css("display"), "Passed!");
});



/**
 * queue-intersection.js
 */
QUnit.test("queue-intersection.queueIntersection, no files", function (assert) {
	// Create test objects
	var kmzFile = [],
		kmzFileId = "#kmzFile",
		kmzFileName = "kmzFile",
		pointFiles = [],
		pointFilesId = "#pointFiles",
		pointFilesName = "pointFiles",
		areaFiles = [],
		areaFilesId = "#areaFiles",
		areaFilesName = "areaFiles",
		countyShpFiles = [],
		countyShpFilesId = "#countyShpFiles",
		countyShpFilesName = "countyShpFiles",
		countyExcelFiles = [],
		countyExcelFilesId = "#countyExcelFiles",
		countyExcelFilesName = "countyExcelFiles",
		urlCalled = "../rtfapp/queue-intersection/";

	$(kmzFileId).prop("files", kmzFile);
	$(pointFilesId).prop("files", pointFiles);
	$(areaFilesId).prop("files", areaFiles);
	$(countyShpFilesId).prop("files", countyShpFiles);
	$(countyExcelFilesId).prop("files", countyExcelFiles);

	mockAjaxCall();

	// Perform test
	queueIntersection();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
});

QUnit.test("queue-intersection.queueIntersection, all files", function (assert) {
	// Create test objects
	var kmzFile = [{name: "kmzFile.kmz"}],
		kmzFileId = "#kmzFile",
		kmzFileName = "kmzFile",
		pointFiles = [{name: "pointFiles.zip"}],
		pointFilesId = "#pointFiles",
		pointFilesName = "pointFiles",
		areaFiles = [{name: "areaFiles.zip"}],
		areaFilesId = "#areaFiles",
		areaFilesName = "areaFiles",
		countyShpFiles = [{name: "countyShpFiles.zip"}],
		countyShpFilesId = "#countyShpFiles",
		countyShpFilesName = "countyShpFiles",
		countyExcelFiles = [{name: "countyExcepFiles.zip"}],
		countyExcelFilesId = "#countyExcelFiles",
		countyExcelFilesName = "countyExcelFiles",
		urlCalled = "../rtfapp/queue-intersection/";

	$(kmzFileId).prop("files", kmzFile);
	$(pointFilesId).prop("files", pointFiles);
	$(areaFilesId).prop("files", areaFiles);
	$(countyShpFilesId).prop("files", countyShpFiles);
	$(countyExcelFilesId).prop("files", countyExcelFiles);

	mockAjaxCall();

	// Perform test
	queueIntersection();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
});

QUnit.test("queue-intersection.queueIntersection, all files error", function (assert) {
	// Create test objects
	var kmzFile = [{name: "kmzFile.kmz"}],
		kmzFileId = "#kmzFile",
		kmzFileName = "kmzFile",
		pointFiles = [{name: "pointFiles.zip"}],
		pointFilesId = "#pointFiles",
		pointFilesName = "pointFiles",
		areaFiles = [{name: "areaFiles.zip"}],
		areaFilesId = "#areaFiles",
		areaFilesName = "areaFiles",
		countyShpFiles = [{name: "countyShpFiles.zip"}],
		countyShpFilesId = "#countyShpFiles",
		countyShpFilesName = "countyShpFiles",
		countyExcelFiles = [{name: "countyExcepFiles.zip"}],
		countyExcelFilesId = "#countyExcelFiles",
		countyExcelFilesName = "countyExcelFiles",
		urlCalled = "../rtfapp/queue-intersection/";

	$(kmzFileId).prop("files", kmzFile);
	$(pointFilesId).prop("files", pointFiles);
	$(areaFilesId).prop("files", areaFiles);
	$(countyShpFilesId).prop("files", countyShpFiles);
	$(countyExcelFilesId).prop("files", countyExcelFiles);

	mockAjaxCall();

	// Perform test
	queueIntersection();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Error
	ajaxRequest.error("error", "error", null);
});

QUnit.test("queue-intersection.queueIntersection, success with errors", function (assert) {
	// Create test objects
	var kmzFile = [{name: "kmzFile.kmz"}],
		kmzFileId = "#kmzFile",
		kmzFileName = "kmzFile",
		pointFiles = [{name: "pointFiles.zip"}],
		pointFilesId = "#pointFiles",
		pointFilesName = "pointFiles",
		areaFiles = [{name: "areaFiles.zip"}],
		areaFilesId = "#areaFiles",
		areaFilesName = "areaFiles",
		countyShpFiles = [{name: "countyShpFiles.zip"}],
		countyShpFilesId = "#countyShpFiles",
		countyShpFilesName = "countyShpFiles",
		countyExcelFiles = [{name: "countyExcepFiles.zip"}],
		countyExcelFilesId = "#countyExcelFiles",
		countyExcelFilesName = "countyExcelFiles",
		urlCalled = "../rtfapp/queue-intersection/",
		queueErrorMessageId = "#queueErrorMessage",
		taskId = -1,
		errors = ["Error 1!", "Error 2?", "Error error."],
		successData = {taskId: taskId, errors: errors},
		expectedErrorMessage = errors.reduce(function (pv, cv) {
			return pv + cv + "<br>";
		}, ""), 
		queueIntersectionMessageId = "intersectionQueueMessage";

	$(kmzFileId).prop("files", kmzFile);
	$(pointFilesId).prop("files", pointFiles);
	$(areaFilesId).prop("files", areaFiles);
	$(countyShpFilesId).prop("files", countyShpFiles);
	$(countyExcelFilesId).prop("files", countyExcelFiles);

	mockAjaxCall();
	$(queueErrorMessageId).html("");
	document.getElementById(queueIntersectionMessageId).innerHTML = "";

	// Perform test
	queueIntersection();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Success
	ajaxRequest.success(successData);
	assert.ok(expectedErrorMessage === $(queueErrorMessageId).html(), "Passed!");
});

QUnit.test("queue-intersection.queueIntersection, success with taskId", function (assert) {
	// Create test objects
	var kmzFile = [{name: "kmzFile.kmz"}],
		kmzFileId = "#kmzFile",
		kmzFileName = "kmzFile",
		pointFiles = [{name: "pointFiles.zip"}],
		pointFilesId = "#pointFiles",
		pointFilesName = "pointFiles",
		areaFiles = [{name: "areaFiles.zip"}],
		areaFilesId = "#areaFiles",
		areaFilesName = "areaFiles",
		countyShpFiles = [{name: "countyShpFiles.zip"}],
		countyShpFilesId = "#countyShpFiles",
		countyShpFilesName = "countyShpFiles",
		countyExcelFiles = [{name: "countyExcepFiles.zip"}],
		countyExcelFilesId = "#countyExcelFiles",
		countyExcelFilesName = "countyExcelFiles",
		urlCalled = "../rtfapp/queue-intersection/",
		queueErrorMessageId = "#queueErrorMessage",
		taskId = 127,
		errors = [],
		successData = {taskId: taskId, errors: errors},
		queueIntersectionMessageId = "intersectionQueueMessage",
		expectedIntersectionMessage = "Extracting Parcels...";

	$(kmzFileId).prop("files", kmzFile);
	$(pointFilesId).prop("files", pointFiles);
	$(areaFilesId).prop("files", areaFiles);
	$(countyShpFilesId).prop("files", countyShpFiles);
	$(countyExcelFilesId).prop("files", countyExcelFiles);

	mockAjaxCall();
	$(queueErrorMessageId).html("");
	document.getElementById(queueIntersectionMessageId).innerHTML = "";

	// Perform test
	queueIntersection();

	var ajaxRequest = mockAjaxPOSTRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");
	assert.ok(undefined === mockAjaxGETRequests[urlCalled], "Passed!");

	// Success
	ajaxRequest.success(successData);
	assert.ok(undefined !== getCurrentIntersection(), "Passed!");
	assert.ok(taskId === getCurrentIntersection().taskId, "Passed!");

	// Displays
	assert.ok(expectedIntersectionMessage === document.getElementById(queueIntersectionMessageId).innerHTML, "Passed!");

	// Monitor progress called
	assert.ok(undefined !== mockAjaxGETRequests[urlCalled], "Passed!");
});

QUnit.test("queue-intersection.toggleTrailUpload, upload form closed", function (assert) {
	// Create test objects
	var open = false,
		uploadTrailFormId = "uploadTrailForm",
		mapWrapperId = "mapWrapper",
		backToMapButtonId = "backToMapButton",
		uploadTrailButtonId = "uploadTrailButton";
	setUploadFormOpen(open);

	setCSSById(uploadTrailFormId, "display", "none");
	setCSSById(mapWrapperId, "display", "block");
	setCSSById(backToMapButtonId, "display", "none");
	setCSSById(uploadTrailButtonId, "display", "block");

	// Perform test
	toggleTrailUpload();

	assert.ok(!open === getUploadFormOpen(), "Passed!");
	assert.ok("block" === $("#" + uploadTrailFormId).css("display"), "Passed!");
	assert.ok("none" === $("#" + mapWrapperId).css("display"), "Passed!");
	assert.ok("block" === $("#" + backToMapButtonId).css("display"), "Passed!");
	assert.ok("none" === $("#" + uploadTrailButtonId).css("display"), "Passed!");
});

QUnit.test("queue-intersection.toggleTrailUpload, upload form open", function (assert) {
	// Create test objects
	var open = true,
		uploadTrailFormId = "uploadTrailForm",
		mapWrapperId = "mapWrapper",
		backToMapButtonId = "backToMapButton",
		uploadTrailButtonId = "uploadTrailButton";
	setUploadFormOpen(open);

	setCSSById(uploadTrailFormId, "display", "block");
	setCSSById(mapWrapperId, "display", "none");
	setCSSById(backToMapButtonId, "display", "block");
	setCSSById(uploadTrailButtonId, "display", "none");

	// Perform test
	toggleTrailUpload();

	assert.ok(!open === getUploadFormOpen(), "Passed!");
	assert.ok("none" === $("#" + uploadTrailFormId).css("display"), "Passed!");
	assert.ok("block" === $("#" + mapWrapperId).css("display"), "Passed!");
	assert.ok("none" === $("#" + backToMapButtonId).css("display"), "Passed!");
	assert.ok("block" === $("#" + uploadTrailButtonId).css("display"), "Passed!");
});

QUnit.test("queue-intersection.monitorProgress, error", function (assert) {
	// Create test objects
	var urlCalled = "../rtfapp/queue-intersection/";

	mockAjaxCall();

	// Perform test
	monitorProgress();

	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Error
	ajaxRequest.error(null, "error", "error");
});

QUnit.test("queue-intersection.monitorProgress, success with valid taskId", function (assert) {
	// Create test objects
	var urlCalled = "../rtfapp/queue-intersection/",
		taskId = 127,
		parcelsExtracted = true,
		placemarksCompleted = 37,
		placemarks = 144,
		placemarkAvgTime = 3,
		started = new Date().toString(),
		successData = {
			taskId: taskId,
			parcelsExtracted: parcelsExtracted,
			placemarksCompleted: placemarksCompleted,
			placemarks: placemarks,
			placemarkAvgTime: placemarkAvgTime,
			started: started
		},
		timeoutTime = 5000,
		expectedPercentStr = "25.69",
		expectedPercent = 25.69,
		expectedRemaining = "5 minutes";

	mockAjaxCall();
	mockTimeouts();

	// Perform test
	monitorProgress();

	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Success with taskId
	ajaxRequest.success(successData);

	// Updated display
	assert.ok(expectedPercentStr + "%" === document.getElementById("intersectionPercentComplete").innerHTML, "Passed!");
	assert.ok(assertDoubleCloseEnough(expectedPercent, $("#intersectionProgressBar").attr("aria-valuenow")), "Passed!");
	assert.ok("Approximately " + expectedRemaining + " Remaining" === document.getElementById("intersectionQueueMessage").innerHTML, "Passed!");

	// Set timeout
	assert.ok(1 === timeouts.length, "Passed!");
	assert.ok(timeoutTime === timeouts[0].time, "Passed!");
});

QUnit.test("queue-intersection.monitorProgress, success with no taskId", function (assert) {
	// Create test objects
	var urlCalled = "../rtfapp/queue-intersection/",
		successData = {};

	mockAjaxCall();
	mockTimeouts();

	setCSSById("noQueuedIntersection", "display", "none");
	setCSSById("queuedIntersection", "display", "block");

	// Perform test
	monitorProgress();

	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Success with taskId
	ajaxRequest.success(successData);

	// Display intersection completed
	assert.ok("block" === $("#noQueuedIntersection").css("display"), "Passed!");
	assert.ok("none" === $("#queuedIntersection").css("display"), "Passed!");
});

QUnit.test("queue-intersection.checkIfInProgress, error", function (assert) {
	// Create test objects
	var urlCalled = "../rtfapp/queue-intersection/";

	mockAjaxCall();

	// Perform test
	checkIfInProgress();

	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Error
	ajaxRequest.error(null, "error", "error");
});

QUnit.test("queue-intersection.checkIfInProgress, success with valid taskId", function (assert) {
	// Create test objects
	var urlCalled = "../rtfapp/queue-intersection/",
		taskId = 127,
		parcelsExtracted = true,
		placemarksCompleted = 37,
		placemarks = 144,
		placemarkAvgTime = 3,
		started = new Date().toString(),
		successData = {
			taskId: taskId,
			parcelsExtracted: parcelsExtracted,
			placemarksCompleted: placemarksCompleted,
			placemarks: placemarks,
			placemarkAvgTime: placemarkAvgTime,
			started: started
		},
		timeoutTime = 5000,
		expectedPercentStr = "25.69",
		expectedPercent = 25.69,
		expectedRemaining = "5 minutes";

	mockAjaxCall();
	mockTimeouts();

	setCSSById("noQueuedIntersection", "display", "block");
	setCSSById("queuedIntersection", "display", "none");

	// Perform test
	checkIfInProgress();

	var ajaxRequest = mockAjaxGETRequests[urlCalled];
	assert.ok(undefined !== ajaxRequest, "Passed!");

	// Success with taskId
	ajaxRequest.success(successData);

	// Display progress
	assert.ok("none" === $("#noQueuedIntersection").css("display"), "Passed!");
	assert.ok("block" === $("#queuedIntersection").css("display"), "Passed!");

	// Updated display
	assert.ok(expectedPercentStr + "%" === document.getElementById("intersectionPercentComplete").innerHTML, "Passed!");
	assert.ok(assertDoubleCloseEnough(expectedPercent, $("#intersectionProgressBar").attr("aria-valuenow")), "Passed!");
	assert.ok("Approximately " + expectedRemaining + " Remaining" === document.getElementById("intersectionQueueMessage").innerHTML, "Passed!");

	// Set timeout
	assert.ok(1 === timeouts.length, "Passed!");
	assert.ok(timeoutTime === timeouts[0].time, "Passed!");
});

QUnit.test("queue-intersection.displayProgress", function (assert) {
	// Create test objects
	setCSSById("noQueuedIntersection", "display", "block");
	setCSSById("queuedIntersection", "display", "none");

	setCSSById("noQueuedIntersection", "display", "block");
	setCSSById("queuedIntersection", "display", "none");
	$("#intersectionPercentComplete").html("");
	$("#intersectionProgressBar").attr("aria-valuenow", "");
	$("#intersectionQueueMessage").html("");

	// Perform test
	displayProgress();

	// Display progress
	assert.ok("none" === $("#noQueuedIntersection").css("display"), "Passed!");
	assert.ok("block" === $("#queuedIntersection").css("display"), "Passed!");
	assert.ok("0.00%" === document.getElementById("intersectionPercentComplete").innerHTML, "Passed!");
	assert.ok("0" === $("#intersectionProgressBar").attr("aria-valuenow"), "Passed!");
	assert.ok("Extracting Parcels..." == document.getElementById("intersectionQueueMessage").innerHTML, "Passed!");
});

QUnit.test("queue-intersection.updateDisplayProgress, with time", function (assert) {
	// Create test objects
	var taskId = 999,
		parcelsExtracted = true,
		placemarksCompleted = 3,
		placemarks = 10,
		placemarkAvgTime = 7000,
		started = new Date().toString(),
		intersection = {
			taskId: taskId,
			parcelsExtracted: parcelsExtracted,
			placemarksCompleted: placemarksCompleted,
			placemarks: placemarks,
			placemarkAvgTime: placemarkAvgTime,
			started: started
		},
		expectedPercentStr = "30.00",
		expectedPercent = 30.00,
		expectedRemaining = "13 hours and 36 minutes";

	setCurrentIntersection(intersection);

	// Perform test
	updateDisplayProgress();

	assert.ok(expectedPercentStr + "%" === document.getElementById("intersectionPercentComplete").innerHTML, "Passed!");
	assert.ok(assertDoubleCloseEnough(expectedPercent, $("#intersectionProgressBar").attr("aria-valuenow")), "Passed!");
	assert.ok("Approximately " + expectedRemaining + " Remaining" === document.getElementById("intersectionQueueMessage").innerHTML, "Passed!");
});

QUnit.test("queue-intersection.updateDisplayProgress, without time", function (assert) {
	// Create test objects
	var taskId = 999,
		parcelsExtracted = true,
		placemarksCompleted = 0,
		placemarks = 10,
		placemarkAvgTime = null,
		started = new Date().toString(),
		intersection = {
			taskId: taskId,
			parcelsExtracted: parcelsExtracted,
			placemarksCompleted: placemarksCompleted,
			placemarks: placemarks,
			placemarkAvgTime: placemarkAvgTime,
			started: started
		},
		expectedPercentStr = "0.00",
		expectedPercent = 0.00,
		expectedRemaining = "13 hours and 36 minutes";

	setCurrentIntersection(intersection);

	// Perform test
	updateDisplayProgress();

	assert.ok(expectedPercentStr + "%" === document.getElementById("intersectionPercentComplete").innerHTML, "Passed!");
	assert.ok(assertDoubleCloseEnough(expectedPercent, $("#intersectionProgressBar").attr("aria-valuenow")), "Passed!");
	assert.ok("Time Remaining Cannot Yet Be Determined" === document.getElementById("intersectionQueueMessage").innerHTML, "Passed!");
});

QUnit.test("queue-intersection.displayIntersectionComplete", function (assert) {
	// Create test objects
	setCSSById("noQueuedIntersection", "display", "none");
	setCSSById("queuedIntersection", "display", "block");

	// Perform test
	displayIntersectionComplete();

	// Display progress
	assert.ok("block" === $("#noQueuedIntersection").css("display"), "Passed!");
	assert.ok("none" === $("#queuedIntersection").css("display"), "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, negative number", function (assert) {
	// Create test objects
	var seconds = -123,
		expectedResult = "0 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, zero seconds", function (assert) {
	// Create test objects
	var seconds = 0,
		expectedResult = "0 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 59 seconds", function (assert) {
	// Create test objects
	var seconds = 59,
		expectedResult = "0 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 60 seconds", function (assert) {
	// Create test objects
	var seconds = 60,
		expectedResult = "1 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 119 seconds", function (assert) {
	// Create test objects
	var seconds = 119,
		expectedResult = "1 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 120 seconds", function (assert) {
	// Create test objects
	var seconds = 129,
		expectedResult = "2 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 3599 seconds", function (assert) {
	// Create test objects
	var seconds = 3599,
		expectedResult = "59 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 3600 seconds", function (assert) {
	// Create test objects
	var seconds = 3600,
		expectedResult = "1 hours and 0 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 7199 seconds", function (assert) {
	// Create test objects
	var seconds = 7199,
		expectedResult = "1 hours and 59 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});

QUnit.test("queue-intersection.formatSecsRemaining, 7200 seconds", function (assert) {
	// Create test objects
	var seconds = 7200,
		expectedResult = "2 hours and 0 minutes";

	// Perform test
	var result = formatSecsRemaining(seconds);

	assert.ok(expectedResult === result, "Passed!");
});