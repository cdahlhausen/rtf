/**
 * Attach a mouseover tooltip with content html to a polygon on a given google map
 * 
 */

currentparcel = -1;

var ParcelApi = function () {
    var statusUrl = "../rtfapp/parcels/statuses/";
    return {
        getParcels: function (filterType, within, callback) {
            $.ajax({
                url: "../rtfapp/parcels/",
                type: "GET",
                data: {
                    filter: filterType,
                    within: within
                },
                success: callback
            });
        }, 
        saveParcel: function (parcel, callback) {
            $.ajax({
                url: "../rtfapp/parcels/",
                type: "POST",
                data: parcel, 
                success: callback,
                error: console.error
            });
        },
        getParcelStatuses: function (callback) {
            $.ajax({
                url: "../rtfapp/parcels/statuses/",
                type: 'GET',
                success: callback
            });
        },
        saveParcelStatus: function (status, callback) {
            var url = "../rtfapp/parcels/statuses/";

            if (status.id != undefined) 
                url += status.id + '/';

            $.ajax({
                url: url,
                type: "POST",
                data: status,
                success: callback
            });
        },
        deleteParcelStatus: function (id, callback) {
            $.ajax({
                url: "../rtfapp/parcels/statuses/" + id + '/',
                type: 'DELETE',
                statusCode: {
                    204: callback,
                    403: function () {
                      alert("You may not delete that status.")
                    }
                }
            });
        }
    };
}();

var ParcelApp = function () {
    var statusView = 'choose',
        statusSelector = $('#parcelStatusSelect'),
        currentParcel,
        statuses;

    function refreshStatuses (id) {
        ParcelApi.getParcelStatuses(function (json) {
            var output = [];
            statuses = json;
            json.forEach(function(status) {
                output.push('<option value="' + status.id + '">' + status.label + '</option>');
            });
            $('#parcelStatusSelect').html(output.join('\n'));
            if (typeof id == 'number')
                $("#parcelStatusSelect option[value='" + id + "']").prop('selected', true);
        });
    }

    function setStatusView (mode) {
            statusView = mode;
            $('#parcelStatusNew').hide();
            $('#parcelStatusChoose').hide();
            $('#parcelStatusEdit').hide();

            switch (mode) {
                case 'new':
                    $('#parcelStatusNew').show();
                    break;
                case 'choose':
                    $('#parcelStatusChoose').show();
                    break;
                case 'edit':
                    
                    var status = statuses.find(function (s) {
                        return s.id == statusSelector.val();
                    });
                    $('#editStatusColor').val(status.color).css('background-color', status.color);
                    $('#editStatusLabel').val(status.label);
                    $('#parcelStatusEdit').show();
            }
    }

    return {
        init: function () {
            refreshStatuses();
        },

        setStatusView: setStatusView,
        
        createStatus: function () {
            var status = {
                label: $('#newStatusLabel').val(),
                color: '#' + $('#newStatusColor').val()
            };
            if (status.name != '' && status.color.length == 7) {
                ParcelApi.saveParcelStatus(status, function (data) {
                    // set selector to this
                    refreshStatuses(data.id);
                    setStatusView('choose');
                    
                });
            }
        },
        deleteStatus: function () {
            var id = statusSelector.val();

            ParcelApi.deleteParcelStatus(id, function () {
                // id will be this parcel's status or first status in list

                refreshStatuses(currentParcel.id);
                filterParcels();
            });
        },
        setCurrentParcel: function (parcel) {
            currentParcel = parcel;
        },
        updateStatus: function () {
            var id = statusSelector.val(),
                status = {
                    id: id,
                    label: $('#editStatusLabel').val(),
                    color: '#' + $('#editStatusColor').val()
                }

            if (status.name != '' && status.color.length == 7) {
                ParcelApi.saveParcelStatus(status, function (data) {
                    // set selector to this
                    refreshStatuses(data.id);
                    setStatusView('choose');
                    filterParcels();
                });
            }
        }
    }
}();

// var ParcelViewModel = function () {

// }


ParcelApp.init();

// ParcelApi.getParcelStatuses(function(json) {
//     // model.statuses = json;
//     var output = [];
//     json.forEach(function(status) {
//         output.push('<option value="' + status.id + '">' + status.label + '</option>');
//     });
//     $('#parcelStatusSelect').html(output.join('\n'));
// });

var updateCurrentParcelDisplay = function() {
  if(currentparcel === -1) { return; }
  var currentParcel = parcels.find(function (p) {
    return p.id == currentparcel;
  });
  ParcelApp.setCurrentParcel(currentParcel);
  ["owner", "permissions", "notes", "address", "type"].forEach(function (id) { 
    $("#parcel-" + id).html(currentParcel[id]); 
  });

  $('#parcel-status').html(currentParcel.status.label);
  $("#parcelStatusSelect option[value='" + currentParcel.status.id + "']").prop('selected', true)

}

function attachPolygonTooltip(polygon, html, map) {
  // Creat tooltip
  polygon.infoWindow = new google.maps.InfoWindow({
    content: html,
  });

  // Mouseover to display tooltip
  google.maps.event.addListener(polygon, 'mouseover', function(e) {
    // slightly above mouse
    var adjustedLatLng = new google.maps.LatLng({lat: e.latLng.lat() + 0.0005, lng: e.latLng.lng()});
    this.setOptions({fillOpacity:0.1});
    polygon.infoWindow.setPosition(adjustedLatLng);
    polygon.infoWindow.open(map);
  });

  // Mouseout to remove tooltip
  google.maps.event.addListener(polygon, 'mouseout', function() {
    this.setOptions({fillOpacity:0.35});
    polygon.infoWindow.close();
  });
}

/**
 * Create a polygon array given a parcel array and google map
 */
//todo: add address, stroke color dependent on legal status
function createParcelPolygons (parcels, map) {
  return parcels.map(function(parcel) {
    var polygon = new google.maps.Polygon({
      paths: parcel.points.map(function(e) {return {
        lat: +e.lat,
        lng: +e.lng
      };}),
      strokeColor: parcel.status.color,
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: parcel.status.color,
      fillOpacity: 0.35,
      zIndex: 0
    });

    google.maps.event.addListener(polygon, "click", function (e) {
        console.log ( 'Parcel was clicked' );
        currentparcel = parcel.id;
        // Check for maintenance requests
        if (prioritizeMaintenaceRequestClicks) {
          maintenanceRequestClicked(e);
          return;
        }
        updateCurrentParcelDisplay();
        displayParcelInfo(parcel)
    });

    var html = '<strong>Owner: ' + parcel.owner + '</strong>';
    // attachPolygonTooltip(polygon, html, map);
    return polygon;
  });
}

/**
 * Toggle parcel layer on map to flag
 */
function toggleParcelLayer(polygons, map, flag) {
  polygons.forEach(function(polygon) {
    if (flag) {
      polygon.setMap(map);
    } else {
      polygon.setMap(null);
    }
  })
}

// Variables to store parcel polygons
// and whether or not to display them
var polygons = undefined,
    showParcels = false;

/**
 * Load polygons from parcels and toggle the map
 */
function loadParcels(parcels, map) {
  polygons = createParcelPolygons(parcels, map);
  showParcels = true;
  toggleParcelLayer(polygons, map, true);
}

$("#parcelSelect").change(parcelSelectToggle);

//todo: refactor globals or something
function toggleParcels() {
  var toggleBtn = $('#toggleParcelBtn');
  showParcels = !showParcels;
  toggleParcelLayer(polygons, map, showParcels);
  if (showParcels) {
    $('#parcelControls').show();
    toggleBtn.html('Hide Parcels');
  } else {
    $('#parcelControls').hide();
    toggleBtn.html('Show Parcels');
  }
}

function filterParcels() {
    var filterType = document.getElementById("parcelSelect").value,
        within = document.getElementById("parcelDistance").value;

    toggleParcelLayer(polygons, map, false);

    ParcelApi.getParcels(filterType, within, function (json) {
        parcels = json;
        polygons = createParcelPolygons(json, map);
        toggleParcelLayer(polygons, map, true);
        updateCurrentParcelDisplay();
    });
}

function parcelSelectToggle() {
  var filterType = document.getElementById("parcelSelect").value,
    withinInput = document.getElementById("parcelDistance");

  withinInput.disabled = !(filterType == 'within')
}



var displayParcelInfo = function (parcel) {
  console.log(parcel)
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#trailDataEditContent").hide();
  $("#trailDataWithContent").hide();
  $("#trailDataWithoutContent").hide();
  $("#parcelDataWithContent").show();

  ["owner", "address", "type", "permissions", "notes"].forEach(
    function (id) { $("#parcel-" + id).html(parcel[id]); 
  });

  $('#parcel-status').html(parcel.status.label);

  updateCurrentParcelDisplay();
}


var editParcelInfo = function () {
  // Add edit content to fields
  ["owner", "address", "type", "permissions", "notes"].forEach(function (id) { $("#edit-parcel-" + id).val($("#parcel-" + id).text());});

  // Add status info 

  // Change views
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#parcelDataWithContent").hide();
  $("#parcelDataEditContent").show();
};

var cancelParcelInfo = function () {
  // Change views
  if (typeof(hideOtherViews) === "function") {
    hideOtherViews();
  }
  $("#parcelDataEditContent").hide();
  $("#parcelDataWithContent").show();
}

var saveParcelInfo = function () {
    var payload = {
    "id": currentparcel
    };
    ["owner", "address", "type", "permissions", "notes"].forEach(function (id) { payload[id] = $("#edit-parcel-" + id).val(); });
    payload['status'] = $('#parcelStatusSelect').val();
    
    ParcelApi.saveParcel(payload, function (data) {
        if (data.success !== undefined && data.success) {
            filterParcels();
        } else {
            console.error("Unable to save!");
        }
    });

    if (typeof(hideOtherViews) === "function") {
        hideOtherViews();
    }
    $("#parcelDataEditContent").hide();
    $("#parcelDataWithContent").show();
}

