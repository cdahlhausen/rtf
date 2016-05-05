function initialize() {
  getPlacemarks();
}
var placemarks = [],
    currentPlacemark = -1;


var getPlacemarks = function() {
  $.ajax({
    url: "../rtfapp/placemarks/",
    type: "GET",
    success: function(json) {
      placemarks = json
      console.log(placemarks);
      mapPoints();
      updateCurrentTrailDisplay();
    }
  });
}

var updateCurrentTrailDisplay = function() {
  if(currentPlacemark === -1) { return; }
  var currentTrail = placemarks.placemarks[currentPlacemark];
  if(currentTrail === undefined) { return; }
  ["name", "description", "status", "current_conditions"].forEach(function (id) { 
    $("#trail-" + id).html(currentTrail[id]); 
  });
}

var displayTrail = function (trailIndex) {
  if (trailIndex < 0 || trailIndex > placemarks.length) {
    console.error("Invalid trail index referenced");
    return;
  }

  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#trailDataWithoutContent").hide();
  $("#trailDataEditContent").hide();
  $("#parcelDataWithContent").hide();
  $("#trailDataWithContent").show();
  currentPlacemark = trailIndex;

  updateCurrentTrailDisplay();
};

var mapPoints = function(){
  // Clear map
  //map = new google.maps.Map(document.getElementById('googleMap'), mapOptions)

  // Clear map trails (for refresh)
  trailpathsOnMap.forEach(function (trailpath) {
    trailpath.setMap(null);
  });
  trailpathsOnMap = [];

  var currentPlacemarkIndex = 0;
  placemarks.placemarks.forEach(function(pm) {
    // Keep track of segments

    pm.lines.forEach(function(currentLine) {
      var points = [];
      currentLine.forEach(function (point) {
        points.push(point);
      });

      var trailpath = new google.maps.Polyline({
        path: points,
        geodesic: true,
        strokeColor: pm.styleColor,
        strokeOpacity: 1.0,
        strokeWeight: pm.styleSize,
        zIndex: 1
      });
      trailpath.index = currentPlacemarkIndex;
      trailpath.setMap(map);

      google.maps.event.addListener(trailpath, "click", function (e) {
        // Check for maintenance requests
        if (prioritizeMaintenaceRequestClicks) {
          maintenanceRequestClicked(e);
          return;
        }

        displayTrail(trailpath.index);
      });

      // Add to global array, used to clear from map
      trailpathsOnMap.push(trailpath);
    });

    // Increment index
    currentPlacemarkIndex++;
  });
};
  
var showPosition = function (position) {
  var userLatLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
  // Do whatever you want with userLatLng.
  var marker = new google.maps.Marker({
      position: userLatLng,
      title: 'Your Location',
      map: map
  });
};

var editTrailInfo = function () {
  // Add edit content to fields
  ["name", "description", "status", "current_conditions"].forEach(function (id) { $("#edit-trail-" + id).val($("#trail-" + id).text());});

  // Change views
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#trailDataWithContent").hide();
  $("#trailDataEditContent").show();
};

var cancelTrailInfo = function () {
  // Change views
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#trailDataEditContent").hide();
  $("#trailDataWithContent").show();
}

var saveTrailInfo = function () {
  var payload = {"id": placemarks.placemarks[currentPlacemark].id};
  ["name", "description", "status", "current_conditions"].forEach(function (id) { payload[id] = $("#edit-trail-" + id).val(); });
  $.ajax({
    url: "../rtfapp/placemarks/",
    type: "POST",
    data: $.param(payload), 
    success: function (data) {
      if (data.success !== undefined && data.success) {
        // Update fields with saved placemark data        
        getPlacemarks();
      } else {
        console.error("Unable to save!");
      }
    },
    error: function (e) {
      console.error(e);
    }
  });
  // Change views
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#trailDataEditContent").hide();
  $("#trailDataWithContent").show();
}