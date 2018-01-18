$( document ).ready(function() {
	var challengeId = $('#container').attr('data-challenge-id');
	var latest_effort = $('#container').attr('data-latest-effort-id');
	var marker;
	var ridePositions = {};

	var $map = $('#route-detail-map');
	
	$.ajax({
		url: "/routes/coordinates/" + routeId,
		type: 'GET',
		success: function(data) {
			coords = JSON.parse(data);
		    map = L.map('route-detail-map', {zoomControl:false,scrollWheelZoom:false,touchZoom:false}).setView([50.736321, -3.536456], 13);

		    L.tileLayer('https://api.mapbox.com/styles/v1/jamesbratt/cjaei11xx66rg2spoci7054wr/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFtZXNicmF0dCIsImEiOiJjaXlsN2kzangwMDFiMzJsamt2ODN2MndzIn0._5ybMQyFC60IomYbpwxBoQ', {
		        attribution: '© OpenStreetMap contributors'
		    }).addTo(map);
		    
		    var route = new L.Polyline(coords, {
		        color: '#EA1595',
		        weight: 6,
		        opacity: 1,
		        smoothFactor: 1
		    });
		    
		    route.addTo(map);
		    map.fitBounds(coords);
		    
		},
		error: function (request, status, error) {
			console.log(error);
		}
	});
	
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Including CSRF token in ajax calls made to Django app
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

	if(challengeId !== undefined) {
		
		$('.compare').on('click', function () {
		    var challengeId = $(this).data("challenge-id")
		    getData(challengeId, true);
		});
		
		$('.clear').on('click', function (e) {
			if(window.effortChart.series.length > 2) {
				window.effortChart.series.slice(2)[0].remove(true);
	            window.effortChart.redraw();		
			} else {
				alert('You cannot clear your latest ride effort.');
			}
		});
		
		function drawMarker(positionIndex) {
			 if(marker == undefined) {
			     marker = L.circleMarker([ridePositions[positionIndex].lng,ridePositions[positionIndex].lat],200, {color:'#EA57BE', fillColor:'#EA57BE', opacity:1}).addTo(map);
			   } else {
			     marker.setLatLng([ridePositions[positionIndex].lng,ridePositions[positionIndex].lat]);
			   }
			   marker.bringToFront();		
		};
		
		var elevationAxisTitle = 'Elevation (m)';
		var speedAxisTitle = 'Speed (km/h)';
		var elevationLabelEnabled = true;
		var speedLabelEnabled = true;
		
		if (window.matchMedia('screen and (max-width: 600px)').matches) {
			elevationAxisTitle = null;
			speedAxisTitle = null;
			elevationLabelEnabled = false;
			speedLabelEnabled = false;
		};
		
		window.effortChart = Highcharts.chart('container', {
	        chart: {
	            type: 'line',
	            zoomType: 'x'
	        },
	        title: false,
	        xAxis: [{
	            crosshair: {
	            	color: '#EA1595',
	            	width: 2,
	            	zIndex: 22,
	            },
	            visible: false
	        }],
		    yAxis: [{
		        labels: {
		            format: '{value}m',
		            enabled: elevationLabelEnabled,
		        },
		        title: {
		            text: elevationAxisTitle,
		        }
		    }, {
		        title: {
		            text: speedAxisTitle,
		        },
		        labels: {
		            format: '{value}km/h',
		            enabled: speedLabelEnabled,
		        },
		        opposite: true
		    }],
		    tooltip: {
		        shared: true,
		        valueDecimals: 2,
		    },
		    plotOptions: {
		        series: {
		            point: {
		                events: {
		                    mouseOver: function () {
		                    	drawMarker(this.x);
		                    }
		                }
		            },
		        }
		    },
	    });
		
		getData(latest_effort, false);
	    
	    function getData(challengeTimeId, isCompare) {
	    	var url;

    		url = "/challenges/ajax-time-stats/" + challengeId + "/?challengeTimeId=" + challengeTimeId;

		    $.ajax({
		        url: url,
		        type: 'GET',
		        beforeSend: function(xhr, settings) {
		          $.ajaxSettings.beforeSend(xhr, settings);
		        },
		        success: function(data) {
		        	var label;
		        	var stats = JSON.parse(data.data);

		        	if(latest_effort == data.id && isCompare === false) {
		        		label = 'Latest Effort';

			            var elevationDataset = {
			                data: [],
			            };
				            
			            $.each(stats, function( index, data ) {
			            	var obj = {}
			            	obj['x'] = index + 1;
			            	obj['y'] = data.elevation;
			            	elevationDataset.data.push(obj);
			            })
		        		
	                    window.effortChart.addSeries({
	                        name: 'Elevation',
	                        type: 'area',
	                        fillColor: '#ECF0F5',
	                        lineWidth: 0,
	                        marker: {
	                        	enabled: false,
	                        },	                    
	                        data: elevationDataset.data
				        });
			            
			            var newDataset = {
			                data: [],
			            };
			            
			            $.each(stats, function( index, data ) {
			            	var obj = {}
			            	obj['x'] = index + 1;
			            	obj['y'] = data.speed;
			            	newDataset.data.push(obj);
			            	ridePositions[index] = {'lat': data.latitude, 'lng': data.longitude};
			            })	
			            
	                    window.effortChart.addSeries({
	                        name: 'Latest',
	                        type: 'line',
	                        yAxis: 1,
	                        marker: {
	                        	enabled: false,
	                        },
	                        data: newDataset.data
				        });
			       
		        	} else if(latest_effort != data.id && isCompare === true) {
		        		label = data.label;

			            var newDataset = { 
			                data: [],
			            };
			            
			            $.each(stats, function( index, data ) {
			            	var obj = {}
			            	obj['x'] = index + 1;
			            	obj['y'] = data.speed;
			            	newDataset.data.push(obj);
			            })	
		        		
	                    window.effortChart.addSeries({
	                        name: label,
	                        type: 'line',
	                        yAxis: 1,
	                        marker: {
	                        	enabled: false,
	                        },
	                        data: newDataset.data
				        });

		        	}
		            
		        },
		        error: function (request, status, error) {
		        	console.log('error');
		        }
		      });
    	  }

	} else {
		$('.compare').remove();
	}
})