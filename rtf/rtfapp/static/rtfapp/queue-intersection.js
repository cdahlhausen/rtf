var currentIntersection = null,
	uploadFormOpen = false;

var queueIntersection = function () {
	var data = new FormData();
	["#kmzFile", "#pointFiles", "#areaFiles", "#countyShpFiles", "#countyExcelFiles"].forEach(function (item) {
		var files = $(item).prop('files');
		if (files.length > 0) {
			data.append($(item).attr("name"), files[0], files[0].name);
		}
	});

	$.ajax({
		url: "../rtfapp/queue-intersection/",
		type: "POST",
		data: data,
		cache: false,
		contentType: false,
		processData: false,
		success: function(data) {
			if (data.taskId !== undefined && data.taskId !== -1) {
				currentIntersection = {
					taskId: data.taskId
				};
				// Hide errors
				$("#queueErrorMessage").html("");
				$("#queueError").hide();
				// Display progress, kick off monitoring
				displayProgress();
				monitorProgress();
			} else if (data.taskId !== undefined && data.errors !== undefined) {
				// Display errors
				var errorMessage = "";
				data.errors.forEach(function (error) {
					errorMessage += error + "<br>";
				});
				$("#queueErrorMessage").html(errorMessage);
				$("#queueError").show();
			}
		},
		error: function(xhr, errmsg, err) {
			console.error("ERROR:" + xhr);
		}
	});
};

var getCurrentIntersection = function () {
	return currentIntersection;
}

var toggleTrailUpload = function() {
	if(uploadFormOpen) {
		$('#uploadTrailForm').hide();
		$('#mapWrapper').show();
		$('#backToMapButton').hide();		
		$('#uploadTrailButton').show();
		uploadFormOpen = false;
	} else {
		$('#mapWrapper').hide();
		$('#uploadTrailForm').show();
		$('#uploadTrailButton').hide();			
		$('#backToMapButton').show();
		uploadFormOpen = true;	
	}
}

var getUploadFormOpen = function () {
	return uploadFormOpen;
}

var setUploadFormOpen = function (open) {
	uploadFormOpen = open;
}

var monitorProgress = function () {
	$.ajax({
		url: "../rtfapp/queue-intersection/",
		type: "GET",
		success: function(data) {
			if (data.taskId != null && data.taskId >= 0) {
				currentIntersection = {
					taskId: data.taskId,
					parcelsExtracted: data.parcelsExtracted,
					placemarksCompleted: data.placemarksCompleted,
					placemarks: data.placemarks,
					placemarkAvgTime: data.placemarkAvgTime,
					started: data.started
				};
				updateDisplayProgress();
				setTimeout(monitorProgress, 5000);
			} else {
				displayIntersectionComplete();
			}
		},
		error: function(xhr, errmsg, err) {
			console.error("ERROR:" + err);
		}
	});
};

// Same as monitorProgress, except specific behavior for
// initially displaying the progress bar
var checkIfInProgress = function () {
	$.ajax({
		url: "../rtfapp/queue-intersection/",
		type: "GET",
		success: function(data) {
			if (data.taskId != null && data.taskId >= 0) {
				displayProgress();
				currentIntersection = {
					taskId: data.taskId,
					parcelsExtracted: data.parcelsExtracted,
					placemarksCompleted: data.placemarksCompleted,
					placemarks: data.placemarks,
					placemarkAvgTime: data.placemarkAvgTime,
					started: data.started
				};
				updateDisplayProgress();
				setTimeout(monitorProgress, 5000);
			}
		},
		error: function(xhr, errmsg, err) {
			console.error("ERROR:" + err);
		}
	});
}

var displayProgress = function () {
	// reset
	$("#intersectionPercentComplete").html("0.00%");
	$("#intersectionProgressBar").attr("aria-valuenow", "0");
	$("#intersectionProgressBar").attr("style", "width: 0%;");
	$("#intersectionQueueMessage").html("Extracting Parcels...");
	// display
	$("#noQueuedIntersection").hide();
	$("#queuedIntersection").show();
};

var setCurrentIntersection = function (intersection) {
	currentIntersection = intersection;
};

var updateDisplayProgress = function () {
	var percent = (100 * currentIntersection.placemarksCompleted / currentIntersection.placemarks).toFixed(2);
	$("#intersectionPercentComplete").html(percent + "%");
	$("#intersectionProgressBar").attr("aria-valuenow", percent);
	$("#intersectionProgressBar").attr("style", "width: " + percent + "%;");

	if (currentIntersection.parcelsExtracted && currentIntersection.placemarkAvgTime != null) {
		// Estimate for time remaining
		var remainingSeconds = currentIntersection.placemarkAvgTime * (currentIntersection.placemarks - currentIntersection.placemarksCompleted);
		$("#intersectionQueueMessage").html("Approximately " + formatSecsRemaining(remainingSeconds) + " Remaining");
	} else if (currentIntersection.parcelsExtracted) {
		// Display unavailable remaining time
		$("#intersectionQueueMessage").html("Time Remaining Cannot Yet Be Determined");
	}
};

var displayIntersectionComplete = function () {
	// display
	$("#queuedIntersection").hide();
	$("#noQueuedIntersection").show();
};

var formatSecsRemaining = function (seconds) {
	// must be non-negative
	seconds = (seconds < 0) ? 0 : seconds;

	// compute hours
	var hours = Math.floor(seconds / 3600);
	seconds -= hours * 3600;

	// compute minutes
	var minutes = Math.floor(seconds / 60);

	// appropriate display
	return (hours > 0) ? hours + " hours and " + minutes + " minutes" : minutes + " minutes";
};